#ifndef INC_ENCODER_H_
#define INC_ENCODER_H_

#include "main.h"
#include <stdint.h>

typedef struct
{
    TIM_HandleTypeDef *htim;
    uint16_t previous_count;
    uint32_t previous_time;
    int8_t forward_sign;
    volatile int32_t total_count;
    volatile int32_t delta_count;
    volatile float speed_mps;
    volatile float speed_kmh;
    volatile float distance_m;
} Encoder_Data;

/* Left: TIM2 (PA0/PA1). Right: TIM1 (PA8/PA9). */
extern Encoder_Data encoder_left;
extern Encoder_Data encoder_right;

HAL_StatusTypeDef Encoder_Start(Encoder_Data *enc,
                                TIM_HandleTypeDef *htim,
                                int8_t forward_sign);
void Encoder_Update(Encoder_Data *enc);

#endif
