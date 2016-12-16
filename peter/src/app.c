/*
 * app.c
 *
 *  Created on: Dec 9, 2015
 *      Author: petera
 */

#include <target.h>
#include <app.h>
#include <miniutils.h>
#include <stm32746g_discovery_ts.h>
#include <Yin.h>


#define ASSERT(x, ...) if (!(x)) { \
  print(__VA_ARGS__); while(1);\
}

ADC_HandleTypeDef adc_hdl;

Yin yin;

//
// SAMPLE FREQUENCY
// PCLK1 = 54MHz
// PCLK1 / ADC_CLOCK_PRESCALER / SAMPLETIME
// 54MHz / 2 / 28 = 964285
// 54MHz / 8 / 144 = 46875
//
#define SPL_FREQ        4000
#define YIN_BUF_SIZE    SPL_FREQ

static void adc_init() {
  GPIO_InitTypeDef          GPIO_InitStruct;

  ADCx_CLK_ENABLE();
  ADCx_CHANNEL_GPIO_CLK_ENABLE();

  GPIO_InitStruct.Pin = ADCx_CHANNEL_PIN;
  GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(ADCx_CHANNEL_GPIO_PORT, &GPIO_InitStruct);

  /*##-1- Configure the ADC peripheral #######################################*/
  adc_hdl.Instance          = ADCx;
  adc_hdl.Init.ClockPrescaler        = ADC_CLOCKPRESCALER_PCLK_DIV8;
  adc_hdl.Init.Resolution            = ADC_RESOLUTION_12B;
  adc_hdl.Init.DataAlign             = ADC_DATAALIGN_RIGHT;
  adc_hdl.Init.ScanConvMode          = DISABLE;                       /* Sequencer disabled (ADC conversion on only 1 channel: channel set on rank 1) */
  adc_hdl.Init.EOCSelection          = DISABLE;
  adc_hdl.Init.ContinuousConvMode    = ENABLE;                        /* Continuous mode disabled to have only 1 conversion at each conversion trig */
  adc_hdl.Init.DMAContinuousRequests = ENABLE;
  adc_hdl.Init.NbrOfConversion       = 1;
  adc_hdl.Init.DiscontinuousConvMode = DISABLE;                       /* Parameter discarded because sequencer is disabled */
  adc_hdl.Init.NbrOfDiscConversion   = 0;
  adc_hdl.Init.ExternalTrigConv      = ADC_SOFTWARE_START;
  adc_hdl.Init.ExternalTrigConvEdge  = ADC_EXTERNALTRIGCONVEDGE_NONE;

  if (HAL_ADC_Init(&adc_hdl) != HAL_OK)
  {
    /* ADC initialization Error */
    ASSERT(FALSE, "adc init err\n");
  }

  /*##-2- Configure ADC regular channel ######################################*/
  ADC_ChannelConfTypeDef sConfig;

  sConfig.Channel      = ADCx_CHANNEL;
  sConfig.Rank         = 1;
  sConfig.SamplingTime = ADC_SAMPLETIME_144CYCLES; //480CYCLES;//ADC_SAMPLETIME_3CYCLES;
  sConfig.Offset       = 0;

  if (HAL_ADC_ConfigChannel(&adc_hdl, &sConfig) != HAL_OK)
  {
    /* Channel Configuration Error */
    ASSERT(FALSE, "adc channel conf err\n");
  }

  HAL_NVIC_SetPriority(ADC_IRQn, 3,0);
  HAL_NVIC_EnableIRQ(ADC_IRQn);
}

static float _work[YIN_BUF_SIZE/2];
static void yin_init(void) {
  Yin_init(&yin, YIN_BUF_SIZE, 0.15, _work);
}


void app_start(void) {
  print("adc init..\n");
  adc_init();
  print("adc init.. OK\n");

  yin_init();

  HAL_ADC_Start_IT(&adc_hdl);
}

void ADC_IRQHandler(void) {
  HAL_ADC_IRQHandler(&adc_hdl);
}

void HAL_ADC_ErrorCallback(ADC_HandleTypeDef *hadc) {
  ASSERT(FALSE, "adc error %08x\n", hadc->ErrorCode);
}

static int16_t min = 0;
static int16_t max = 0;
static int32_t sum = 0;
static int16_t data[YIN_BUF_SIZE];
uint32_t ix = 0;
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc) {
  uint32_t raw = HAL_ADC_GetValue(hadc);
  int16_t v = (int16_t)(raw-0x0800);
  data[ix] = v;
  sum += v;
  min = v < min ? v : min;
  max = v > max ? v : max;
  ix++;
  if (ix >= YIN_BUF_SIZE) {
    float freq = Yin_getPitch(&yin, data);
    print("sum:%6d    min:%4d    max:%4d    avg:%4d    freq:%d %d%%\n",
        sum, min, max, sum/YIN_BUF_SIZE, (int)freq, (int)(100*Yin_getProbability(&yin)));
    max = min = ix = sum = 0;
  }
}

