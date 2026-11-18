#include "encoder.h"

/* Values from the supplied encoder project; calibrate the contact wheels. */
#define ENCODER_PPR       600.0f
#define ENCODER_X4        4.0f
#define COUNTS_PER_REV    (ENCODER_PPR * ENCODER_X4)
#define WHEEL_DIAMETER_M  0.061f
#define PI_F              3.14159265359f
#define SAMPLE_MS         100U

Encoder_Data encoder_left = {0};
Encoder_Data encoder_right = {0};

HAL_StatusTypeDef Encoder_Start(Encoder_Data *enc,
                                TIM_HandleTypeDef *htim,
                                int8_t forward_sign)
{
    if (enc == NULL || htim == NULL)
        return HAL_ERROR;
    if (forward_sign != 1 && forward_sign != -1)
        return HAL_ERROR;

    enc->htim = htim;
    enc->forward_sign = forward_sign;
    __HAL_TIM_SET_COUNTER(htim, 0);
    if (HAL_TIM_Encoder_Start(htim, TIM_CHANNEL_ALL) != HAL_OK)
    {
        enc->htim = NULL;
        return HAL_ERROR;
    }

    enc->previous_count = (uint16_t)__HAL_TIM_GET_COUNTER(htim);
    enc->previous_time = HAL_GetTick();
    enc->total_count = 0;
    enc->delta_count = 0;
    enc->speed_mps = 0.0f;
    enc->speed_kmh = 0.0f;
    enc->distance_m = 0.0f;
    return HAL_OK;
}

void Encoder_Update(Encoder_Data *enc)
{
    uint32_t now;
    uint32_t dt_ms;
    uint16_t current_count;
    uint16_t diff;
    int32_t delta;
    float displacement;

    if (enc == NULL || enc->htim == NULL)
        return;

    now = HAL_GetTick();
    dt_ms = now - enc->previous_time;
    if (dt_ms < SAMPLE_MS)
        return;

    current_count = (uint16_t)__HAL_TIM_GET_COUNTER(enc->htim);
    diff = (uint16_t)(current_count - enc->previous_count);
    delta = (diff < 32768U) ? (int32_t)diff : (int32_t)diff - 65536;
    delta *= enc->forward_sign;
    displacement = ((float)delta / COUNTS_PER_REV) * PI_F * WHEEL_DIAMETER_M;

    enc->delta_count = delta;
    enc->total_count += delta;
    enc->speed_mps = displacement * 1000.0f / (float)dt_ms;
    enc->speed_kmh = enc->speed_mps * 3.6f;
    enc->distance_m += displacement;
    enc->previous_count = current_count;
    enc->previous_time = now;
}
