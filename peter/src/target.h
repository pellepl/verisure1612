/*
 * target.h
 *
 *  Created on: Dec 7, 2015
 *      Author: petera
 */

#ifndef TARGET_H_
#define TARGET_H_

#include <common.h>
#include <system.h>
#include <stm32f7xx_hal_conf.h>
#include <stm32f7xx.h>

#define CONFIG_UART_CNT 1
#define CONFIG_UART3

#define ADCx                            ADC3
#define ADCx_CLK_ENABLE()               __HAL_RCC_ADC3_CLK_ENABLE()
#define ADCx_CHANNEL_GPIO_CLK_ENABLE()  __HAL_RCC_GPIOF_CLK_ENABLE()

#define ADCx_FORCE_RESET()              __HAL_RCC_ADC_FORCE_RESET()
#define ADCx_RELEASE_RESET()            __HAL_RCC_ADC_RELEASE_RESET()

/* Definition for ADCx Channel Pin */
#define ADCx_CHANNEL_PIN                GPIO_PIN_4
#define ADCx_CHANNEL_GPIO_PORT          GPIOF

/* Definition for ADCx's Channel */
#define ADCx_CHANNEL                    ADC_CHANNEL_14


#endif /* TARGET_H_ */
