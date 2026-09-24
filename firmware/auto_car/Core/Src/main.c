/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "stdio.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define ESC_STOP_PULSE_US       1500U
#define BENCH_TIMEOUT_MS        2000U

#define BNO055_I2C_ADDRESS_7BIT  0x28U
#define BNO055_CHIP_ID_REGISTER  0x00U

#define BMP280_I2C_ADDRESS_7BIT  0x76U
#define BMP280_CHIP_ID_REGISTER  0xD0U

#define BNO055_OPR_MODE_REGISTER  0x3DU
#define BNO055_CONFIG_MODE        0x00U
#define BNO055_NDOF_MODE          0x0CU

#define BNO055_EULER_DATA_REGISTER  0x1AU
#define BNO055_EULER_SCALE           16L
#define IMU_OUTPUT_PERIOD_MS         200U

#define BNO055_CALIB_STAT_REGISTER  0x35U
#define CALIB_OUTPUT_PERIOD_MS      1000U

#define BNO055_SYS_STATUS_REGISTER  0x39U
#define BNO055_SYS_ERR_REGISTER     0x3AU
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
I2C_HandleTypeDef hi2c1;

TIM_HandleTypeDef htim3;
TIM_HandleTypeDef htim4;

UART_HandleTypeDef huart2;

/* USER CODE BEGIN PV */

static const uint8_t pong_message[] = "PONG\n";

static uint8_t uart_rx_byte = 0U;
static uint8_t uart_line_buffer[16];
static volatile uint8_t uart_line_length = 0U;
static volatile uint8_t uart_line_ready = 0U;
static uint32_t last_led_tick = 0U;

static volatile uint8_t stop_requested = 0U;
static uint8_t bench_command_active = 0U;
static uint32_t last_bench_command_tick = 0U;

static uint32_t last_imu_tick = 0U;

static uint32_t last_calib_tick = 0U;

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART2_UART_Init(void);
static void MX_TIM3_Init(void);
static void MX_TIM4_Init(void);
static void MX_I2C1_Init(void);
/* USER CODE BEGIN PFP */
static void I2C_Scan(void);
static void Sensor_ReadChipIds(void);
static void BNO055_EnableNDOF(void);
static void BNO055_PrintEuler(void);
static void BNO055_PrintCalibration(void);
static void BNO055_PrintDiagnostics(void);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
static void BNO055_PrintDiagnostics(void)
{
    static const uint8_t read_error[] =
        "BNO055 DIAGNOSTIC READ ERROR\r\n";

    uint8_t system_data[2];
    uint8_t operation_mode = 0U;
    char message[80];
    int message_length;

    if (HAL_I2C_Mem_Read(
            &hi2c1,
            (uint16_t)(BNO055_I2C_ADDRESS_7BIT << 1U),
            BNO055_SYS_STATUS_REGISTER,
            I2C_MEMADD_SIZE_8BIT,
            system_data,
            2U,
            100U) != HAL_OK)
    {
        (void)HAL_UART_Transmit(
            &huart2,
            (uint8_t *)read_error,
            (uint16_t)(sizeof(read_error) - 1U),
            100U);
        return;
    }

    if (HAL_I2C_Mem_Read(
            &hi2c1,
            (uint16_t)(BNO055_I2C_ADDRESS_7BIT << 1U),
            BNO055_OPR_MODE_REGISTER,
            I2C_MEMADD_SIZE_8BIT,
            &operation_mode,
            1U,
            100U) != HAL_OK)
    {
        (void)HAL_UART_Transmit(
            &huart2,
            (uint8_t *)read_error,
            (uint16_t)(sizeof(read_error) - 1U),
            100U);
        return;
    }

    message_length = snprintf(
        message,
        sizeof(message),
        "MODE=0x%02X SYS_STATUS=%u SYS_ERR=0x%02X\r\n",
        (unsigned int)operation_mode,
        (unsigned int)system_data[0],
        (unsigned int)system_data[1]);

    if ((message_length > 0) &&
        (message_length < (int)sizeof(message)))
    {
        (void)HAL_UART_Transmit(
            &huart2,
            (uint8_t *)message,
            (uint16_t)message_length,
            100U);
    }
}

static void I2C_Scan(void)
{
    static const uint8_t hex_digits[] = "0123456789ABCDEF";
    static const uint8_t done_message[] = "I2C SCAN DONE\r\n";
    static const uint8_t none_message[] = "I2C DEVICE NOT FOUND\r\n";

    uint8_t message[] = "I2C 0x00\r\n";
    uint8_t device_found = 0U;
    uint16_t address;

    for (address = 0x08U; address <= 0x77U; address++)
    {
        if (HAL_I2C_IsDeviceReady(
                &hi2c1,
                (uint16_t)(address << 1U),
                2U,
                20U) == HAL_OK)
        {
            device_found = 1U;

            message[6] = hex_digits[(address >> 4U) & 0x0FU];
            message[7] = hex_digits[address & 0x0FU];

            (void)HAL_UART_Transmit(
                &huart2,
                message,
                (uint16_t)(sizeof(message) - 1U),
                100U);
        }
    }

    if (device_found != 0U)
    {
        (void)HAL_UART_Transmit(
            &huart2,
            done_message,
            (uint16_t)(sizeof(done_message) - 1U),
            100U);
    }
    else
    {
        (void)HAL_UART_Transmit(
            &huart2,
            none_message,
            (uint16_t)(sizeof(none_message) - 1U),
            100U);
    }
}

static void Sensor_ReadChipIds(void)
{
    static const uint8_t hex_digits[] = "0123456789ABCDEF";
    static const uint8_t bno_error[] = "BNO055 READ ERROR\r\n";
    static const uint8_t bmp_error[] = "BMP280 READ ERROR\r\n";

    uint8_t bno_message[] = "BNO055 ID: 0x00\r\n";
    uint8_t bmp_message[] = "BMP280 ID: 0x00\r\n";
    uint8_t chip_id = 0U;

    if (HAL_I2C_Mem_Read(
            &hi2c1,
            (uint16_t)(BNO055_I2C_ADDRESS_7BIT << 1U),
            BNO055_CHIP_ID_REGISTER,
            I2C_MEMADD_SIZE_8BIT,
            &chip_id,
            1U,
            100U) == HAL_OK)
    {
        bno_message[13] = hex_digits[(chip_id >> 4U) & 0x0FU];
        bno_message[14] = hex_digits[chip_id & 0x0FU];

        (void)HAL_UART_Transmit(
            &huart2,
            bno_message,
            (uint16_t)(sizeof(bno_message) - 1U),
            100U);
    }
    else
    {
        (void)HAL_UART_Transmit(
            &huart2,
            bno_error,
            (uint16_t)(sizeof(bno_error) - 1U),
            100U);
    }

    chip_id = 0U;

    if (HAL_I2C_Mem_Read(
            &hi2c1,
            (uint16_t)(BMP280_I2C_ADDRESS_7BIT << 1U),
            BMP280_CHIP_ID_REGISTER,
            I2C_MEMADD_SIZE_8BIT,
            &chip_id,
            1U,
            100U) == HAL_OK)
    {
        bmp_message[13] = hex_digits[(chip_id >> 4U) & 0x0FU];
        bmp_message[14] = hex_digits[chip_id & 0x0FU];

        (void)HAL_UART_Transmit(
            &huart2,
            bmp_message,
            (uint16_t)(sizeof(bmp_message) - 1U),
            100U);
    }
    else
    {
        (void)HAL_UART_Transmit(
            &huart2,
            bmp_error,
            (uint16_t)(sizeof(bmp_error) - 1U),
            100U);
    }
}

static void BNO055_EnableNDOF(void)
{
    static const uint8_t hex_digits[] = "0123456789ABCDEF";
    static const uint8_t write_error[] = "BNO055 MODE WRITE ERROR\r\n";
    static const uint8_t read_error[] = "BNO055 MODE READ ERROR\r\n";

    uint8_t message[] = "BNO055 MODE: 0x00\r\n";
    uint8_t mode = BNO055_CONFIG_MODE;

    if (HAL_I2C_Mem_Write(
            &hi2c1,
            (uint16_t)(BNO055_I2C_ADDRESS_7BIT << 1U),
            BNO055_OPR_MODE_REGISTER,
            I2C_MEMADD_SIZE_8BIT,
            &mode,
            1U,
            100U) != HAL_OK)
    {
        (void)HAL_UART_Transmit(
            &huart2,
            write_error,
            (uint16_t)(sizeof(write_error) - 1U),
            100U);
        return;
    }

    HAL_Delay(20U);

    mode = BNO055_NDOF_MODE;

    if (HAL_I2C_Mem_Write(
            &hi2c1,
            (uint16_t)(BNO055_I2C_ADDRESS_7BIT << 1U),
            BNO055_OPR_MODE_REGISTER,
            I2C_MEMADD_SIZE_8BIT,
            &mode,
            1U,
            100U) != HAL_OK)
    {
        (void)HAL_UART_Transmit(
            &huart2,
            write_error,
            (uint16_t)(sizeof(write_error) - 1U),
            100U);
        return;
    }

    HAL_Delay(10U);

    mode = 0U;

    if (HAL_I2C_Mem_Read(
            &hi2c1,
            (uint16_t)(BNO055_I2C_ADDRESS_7BIT << 1U),
            BNO055_OPR_MODE_REGISTER,
            I2C_MEMADD_SIZE_8BIT,
            &mode,
            1U,
            100U) == HAL_OK)
    {
        message[15] = hex_digits[(mode >> 4U) & 0x0FU];
        message[16] = hex_digits[mode & 0x0FU];

        (void)HAL_UART_Transmit(
            &huart2,
            message,
            (uint16_t)(sizeof(message) - 1U),
            100U);
    }
    else
    {
        (void)HAL_UART_Transmit(
            &huart2,
            read_error,
            (uint16_t)(sizeof(read_error) - 1U),
            100U);
    }
}

static void BNO055_PrintEuler(void)
{
    static const uint8_t read_error[] = "BNO055 EULER READ ERROR\r\n";

    uint8_t data[6];
    int16_t heading_raw;
    int16_t roll_raw;
    int16_t pitch_raw;

    int32_t heading_cdeg;
    int32_t roll_cdeg;
    int32_t pitch_cdeg;

    char message[80];
    int message_length;

    if (HAL_I2C_Mem_Read(
            &hi2c1,
            (uint16_t)(BNO055_I2C_ADDRESS_7BIT << 1U),
            BNO055_EULER_DATA_REGISTER,
            I2C_MEMADD_SIZE_8BIT,
            data,
            6U,
            100U) != HAL_OK)
    {
        (void)HAL_UART_Transmit(
            &huart2,
            (uint8_t *)read_error,
            (uint16_t)(sizeof(read_error) - 1U),
            100U);
        return;
    }

    heading_raw = (int16_t)(
        ((uint16_t)data[1] << 8U) |
        (uint16_t)data[0]);

    roll_raw = (int16_t)(
        ((uint16_t)data[3] << 8U) |
        (uint16_t)data[2]);

    pitch_raw = (int16_t)(
        ((uint16_t)data[5] << 8U) |
        (uint16_t)data[4]);

    /*
     * BNO055 produces 16 LSB per degree.
     * Convert to centidegrees:
     * 12345 means 123.45 degrees.
     */
    heading_cdeg =
        ((int32_t)heading_raw * 100L) / BNO055_EULER_SCALE;

    roll_cdeg =
        ((int32_t)roll_raw * 100L) / BNO055_EULER_SCALE;

    pitch_cdeg =
        ((int32_t)pitch_raw * 100L) / BNO055_EULER_SCALE;

    message_length = snprintf(
        message,
        sizeof(message),
        "H_cdeg=%ld R_cdeg=%ld P_cdeg=%ld\r\n",
        (long)heading_cdeg,
        (long)roll_cdeg,
        (long)pitch_cdeg);

    if ((message_length > 0) &&
        (message_length < (int)sizeof(message)))
    {
        (void)HAL_UART_Transmit(
            &huart2,
            (uint8_t *)message,
            (uint16_t)message_length,
            100U);
    }
}

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    if (GPIO_Pin == B1_Pin)
    {
        stop_requested = 1U;
    }
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART2)
    {
        if (uart_line_ready == 0U)
        {
            if (uart_rx_byte == (uint8_t)'\n')
            {
                uart_line_ready = 1U;
            }
            else if (uart_rx_byte != (uint8_t)'\r')
            {
                if (uart_line_length < (uint8_t)sizeof(uart_line_buffer))
                {
                    uart_line_buffer[uart_line_length] = uart_rx_byte;
                    uart_line_length++;
                }
                else
                {
                    uart_line_length = 0U;
                }
            }
        }

        if (HAL_UART_Receive_IT(&huart2, &uart_rx_byte, 1U) != HAL_OK)
        {
            Error_Handler();
        }
    }
}

static void BNO055_PrintCalibration(void)
{
    static const uint8_t read_error[] =
        "BNO055 CALIB READ ERROR\r\n";

    uint8_t calib_status = 0U;
    uint8_t system_status;
    uint8_t gyro_status;
    uint8_t accel_status;
    uint8_t mag_status;

    char message[64];
    int message_length;

    if (HAL_I2C_Mem_Read(
            &hi2c1,
            (uint16_t)(BNO055_I2C_ADDRESS_7BIT << 1U),
            BNO055_CALIB_STAT_REGISTER,
            I2C_MEMADD_SIZE_8BIT,
            &calib_status,
            1U,
            100U) != HAL_OK)
    {
        (void)HAL_UART_Transmit(
            &huart2,
            (uint8_t *)read_error,
            (uint16_t)(sizeof(read_error) - 1U),
            100U);
        return;
    }

    system_status = (calib_status >> 6U) & 0x03U;
    gyro_status   = (calib_status >> 4U) & 0x03U;
    accel_status  = (calib_status >> 2U) & 0x03U;
    mag_status    = calib_status & 0x03U;

    message_length = snprintf(
        message,
        sizeof(message),
        "CAL SYS=%u GYR=%u ACC=%u MAG=%u\r\n",
        (unsigned int)system_status,
        (unsigned int)gyro_status,
        (unsigned int)accel_status,
        (unsigned int)mag_status);

    if ((message_length > 0) &&
        (message_length < (int)sizeof(message)))
    {
        (void)HAL_UART_Transmit(
            &huart2,
            (uint8_t *)message,
            (uint16_t)message_length,
            100U);
    }
}
/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USART2_UART_Init();
  MX_TIM3_Init();
  MX_TIM4_Init();
  MX_I2C1_Init();
  /* USER CODE BEGIN 2 */
	if (HAL_UART_Receive_IT(&huart2, &uart_rx_byte, 1U) != HAL_OK)
	{
    Error_Handler();
	}
	if (HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_2) != HAL_OK)
	{
    Error_Handler();
	}

	HAL_Delay(700);
	I2C_Scan();
	Sensor_ReadChipIds();
	BNO055_EnableNDOF();


	if (HAL_TIM_PWM_Start(&htim4, TIM_CHANNEL_1) != HAL_OK)
	{
    Error_Handler();
	}
  __HAL_TIM_SET_COMPARE(
    &htim4,
    TIM_CHANNEL_1,
    ESC_STOP_PULSE_US
  );
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
	while (1)
	{
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
		if (stop_requested != 0U)
		{
			__HAL_TIM_SET_COMPARE(
					&htim4,
					TIM_CHANNEL_1,
					ESC_STOP_PULSE_US
			);

			bench_command_active = 0U;
			stop_requested = 0U;
		}
		else if ((bench_command_active != 0U) &&
         ((HAL_GetTick() - last_bench_command_tick) >= BENCH_TIMEOUT_MS))
		{
			__HAL_TIM_SET_COMPARE(
					&htim4,
					TIM_CHANNEL_1,
					ESC_STOP_PULSE_US
			);

			bench_command_active = 0U;
		}

		if ((HAL_GetTick() - last_led_tick) >= 500U)
		{
			last_led_tick = HAL_GetTick();
			HAL_GPIO_TogglePin(LD2_GPIO_Port, LD2_Pin);
		}
		if ((HAL_GetTick() - last_imu_tick) >= IMU_OUTPUT_PERIOD_MS)
		{
			last_imu_tick = HAL_GetTick();
			BNO055_PrintEuler();
		}

		if ((HAL_GetTick() - last_calib_tick) >= CALIB_OUTPUT_PERIOD_MS)
		{
			last_calib_tick = HAL_GetTick();
			BNO055_PrintCalibration();
			BNO055_PrintDiagnostics();
		}

		if (uart_line_ready != 0U)
		{
			if ((uart_line_length == 4U) &&
					(uart_line_buffer[0] == (uint8_t)'P') &&
					(uart_line_buffer[1] == (uint8_t)'I') &&
					(uart_line_buffer[2] == (uint8_t)'N') &&
					(uart_line_buffer[3] == (uint8_t)'G'))
			{
					HAL_UART_Transmit(
							&huart2,
							(uint8_t *)pong_message,
							(uint16_t)(sizeof(pong_message) - 1U),
							100U
					);
			}

			uart_line_length = 0U;
			uart_line_ready = 0U;
		}
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI_DIV2;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL16;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief I2C1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_I2C1_Init(void)
{

  /* USER CODE BEGIN I2C1_Init 0 */

  /* USER CODE END I2C1_Init 0 */

  /* USER CODE BEGIN I2C1_Init 1 */

  /* USER CODE END I2C1_Init 1 */
  hi2c1.Instance = I2C1;
  hi2c1.Init.ClockSpeed = 100000;
  hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c1.Init.OwnAddress2 = 0;
  hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN I2C1_Init 2 */

  /* USER CODE END I2C1_Init 2 */

}

/**
  * @brief TIM3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM3_Init(void)
{

  /* USER CODE BEGIN TIM3_Init 0 */

  /* USER CODE END TIM3_Init 0 */

  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};

  /* USER CODE BEGIN TIM3_Init 1 */

  /* USER CODE END TIM3_Init 1 */
  htim3.Instance = TIM3;
  htim3.Init.Prescaler = 63;
  htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim3.Init.Period = 19999;
  htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim3.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_PWM_Init(&htim3) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim3, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 1500;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  if (HAL_TIM_PWM_ConfigChannel(&htim3, &sConfigOC, TIM_CHANNEL_2) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM3_Init 2 */

  /* USER CODE END TIM3_Init 2 */
  HAL_TIM_MspPostInit(&htim3);

}

/**
  * @brief TIM4 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM4_Init(void)
{

  /* USER CODE BEGIN TIM4_Init 0 */

  /* USER CODE END TIM4_Init 0 */

  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};

  /* USER CODE BEGIN TIM4_Init 1 */

  /* USER CODE END TIM4_Init 1 */
  htim4.Instance = TIM4;
  htim4.Init.Prescaler = 63;
  htim4.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim4.Init.Period = 19999;
  htim4.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim4.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_PWM_Init(&htim4) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim4, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 1500;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  if (HAL_TIM_PWM_ConfigChannel(&htim4, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM4_Init 2 */

  /* USER CODE END TIM4_Init 2 */
  HAL_TIM_MspPostInit(&htim4);

}

/**
  * @brief USART2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART2_UART_Init(void)
{

  /* USER CODE BEGIN USART2_Init 0 */

  /* USER CODE END USART2_Init 0 */

  /* USER CODE BEGIN USART2_Init 1 */

  /* USER CODE END USART2_Init 1 */
  huart2.Instance = USART2;
  huart2.Init.BaudRate = 115200;
  huart2.Init.WordLength = UART_WORDLENGTH_8B;
  huart2.Init.StopBits = UART_STOPBITS_1;
  huart2.Init.Parity = UART_PARITY_NONE;
  huart2.Init.Mode = UART_MODE_TX_RX;
  huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart2.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart2) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART2_Init 2 */

  /* USER CODE END USART2_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  /* USER CODE BEGIN MX_GPIO_Init_1 */

  /* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(LD2_GPIO_Port, LD2_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin : B1_Pin */
  GPIO_InitStruct.Pin = B1_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(B1_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : LD2_Pin */
  GPIO_InitStruct.Pin = LD2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(LD2_GPIO_Port, &GPIO_InitStruct);

  /* EXTI interrupt init*/
  HAL_NVIC_SetPriority(EXTI15_10_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);

  /* USER CODE BEGIN MX_GPIO_Init_2 */

  /* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
