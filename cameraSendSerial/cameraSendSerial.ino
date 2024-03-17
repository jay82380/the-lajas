/*
 *  camera.ino - Simple camera example sketch
 *  Copyright 2018, 2022 Sony Semiconductor Solutions Corporation
 *
 *  This library is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU Lesser General Public
 *  License as published by the Free Software Foundation; either
 *  version 2.1 of the License, or (at your option) any later version.
 *
 *  This library is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *  Lesser General Public License for more details.
 *
 *  You should have received a copy of the GNU Lesser General Public
 *  License along with this library; if not, write to the Free Software
 *  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 *  This is a test app for the camera library.
 *  This library can only be used on the Spresense with the FCBGA chip package.
 */

#include <SDHCI.h>
#include <stdio.h>  /* for sprintf */

#include <Camera.h>

#define BAUDRATE (2000000)

/**
 * Print error message
 */
void printError(enum CamErr err)
{
  Serial.print("Error: ");
  switch (err)
    {
      case CAM_ERR_NO_DEVICE:
        Serial.println("No Device");
        break;
      case CAM_ERR_ILLEGAL_DEVERR:
        Serial.println("Illegal device error");
        break;
      case CAM_ERR_ALREADY_INITIALIZED:
        Serial.println("Already initialized");
        break;
      case CAM_ERR_NOT_INITIALIZED:
        Serial.println("Not initialized");
        break;
      case CAM_ERR_NOT_STILL_INITIALIZED:
        Serial.println("Still picture not initialized");
        break;
      case CAM_ERR_CANT_CREATE_THREAD:
        Serial.println("Failed to create thread");
        break;
      case CAM_ERR_INVALID_PARAM:
        Serial.println("Invalid parameter");
        break;
      case CAM_ERR_NO_MEMORY:
        Serial.println("No memory");
        break;
      case CAM_ERR_USR_INUSED:
        Serial.println("Buffer already in use");
        break;
      case CAM_ERR_NOT_PERMITTED:
        Serial.println("Operation not permitted");
        break;
      default:
        break;
    }
}

/**
 * Callback from Camera library when video frame is captured.
 */
void CamCB(CamImage img)
{
  // Wait for image to be ready
  if(img.isAvailable() == false) return;

  // Wait for monitor program to write start signal
  while(Serial.available() <= 0);
  digitalWrite(LED3, LOW);
  char mode = Serial.read();
  if(mode != 'S') return;

  digitalWrite(LED0, HIGH);

  // Convert image to JPG format
  img.convertPixFormat(CAM_IMAGE_PIX_FMT_GRAY);
  // Get data about image
  char *buf = img.getImgBuff();
  int size = img.getImgSize();
  Serial.println(size);

  // Write image to serial port
  for(int i=0; i < size; ++i, ++buf) {
    Serial.write(*buf);
  }

  digitalWrite(LED0, LOW);
  digitalWrite(LED3, HIGH);
}

/**
 * @brief Initialize camera
 */
void setup()
{
  pinMode(LED0, OUTPUT);
  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(LED3, OUTPUT);
  CamErr err;

  /* Open serial communications and wait for port to open */
  Serial.begin(BAUDRATE);
  while (!Serial) {}

  /* begin() without parameters means that
   * number of buffers = 1, 30FPS, QVGA, YUV 4:2:2 format */
  err = theCamera.begin();
  if (err != CAM_ERR_SUCCESS) printError(err);

  // /* Start video stream.
  //  * If received video stream data from camera device,
  //  *  camera library call CamCB.
  //  */
  // digitalWrite(LED3, HIGH);
  // err = theCamera.startStreaming(true, CamCB);
  // if (err != CAM_ERR_SUCCESS) printError(err);

  /* Auto white balance configuration */
  err = theCamera.setAutoWhiteBalanceMode(CAM_WHITE_BALANCE_DAYLIGHT);
  if (err != CAM_ERR_SUCCESS) printError(err);
 
  // Set format (GREYSCALE NOT WORKING)
  err = theCamera.setStillPictureImageFormat(
     CAM_IMGSIZE_QUADVGA_H/2,
     CAM_IMGSIZE_QUADVGA_V/2,
     CAM_IMAGE_PIX_FMT_JPG);
  if (err != CAM_ERR_SUCCESS) printError(err);

  err = theCamera.setJPEGQuality(50);
  if (err != CAM_ERR_SUCCESS) printError(err);
}

/**
 * @brief Take picture with format JPEG per second
 */
void loop()
{
  // Wait for monitor program to be ready
  digitalWrite(LED3, HIGH);
  while(Serial.available() <= 0);
  digitalWrite(LED3, LOW);
  char read = Serial.read();

  if(read == 'S') {
    CamImage img = theCamera.takePicture();

    /* Check availability of the img instance. */
    /* If any errors occur, the img is not available. */
    if (img.isAvailable()) {
      digitalWrite(LED0, HIGH);

      char *buf = img.getImgBuff();
      int size = img.getImgSize();
      Serial.println(size);

      // Write image to serial port
      for(int i=0; i < size; ++i, ++buf) {
        Serial.write(*buf);
      }
      // Serial.write(*buf, size);
      digitalWrite(LED0, LOW);
    } else {
      // Serial.println("Failed to take picture");
      digitalWrite(LED1, HIGH);
    }
  }
}
