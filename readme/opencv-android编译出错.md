#  Android SDK Tools: OpenCV requires Android SDK Tools revision 14 or newer

## Android编译opencv编译出错，提示信息如下
```
-- Android: fixup -g compiler option from Android toolchain
-- Update variable ANDROID_SDK from environment: /home/oskar/.buildozer/android/platform/android-sdk
-- Android SDK Tools: ver. 2.0 (description: 'Android SDK Command-line Tools')
-- Android SDK Build Tools: ver. 30.0.0-rc4 (subdir 30.0.0-rc4 from 30.0.0-rc4)
CMake Error at cmake/android/OpenCVDetectAndroidSDK.cmake:176 (message):
  Android SDK Tools: OpenCV requires Android SDK Tools revision 14 or newer.

  Use BUILD_ANDROID_PROJECTS=OFF to prepare Android project files without
  building them
Call Stack (most recent call first):
  CMakeLists.txt:780 (include)
```
## 解决办法
```
Download cmdlines-tools from google
Create a directory for the android sdk at buildozer android location:
mkdir ~/.buildozer/android/platform/android-sdk
Move the zip to this folder and unzip it
Rename the folder
mv tools old-tools
Install missing dependencies & the famous tools:
sudo ./sdkmanager --sdk_root=/home/<USERNAME>/.buildozer/android/platform/android-sdk/ --install "tools"
sudo ./sdkmanager --sdk_root=/home/<USERNAME>/.buildozer/android/platform/android-sdk/ --install "build-tools;29.0.0-rc3"
sudo ./sdkmanager --sdk_root=/home/<USERNAME>/.buildozer/android/platform/android-sdk/ --install "platforms;android-27"
sudo ./sdkmanager --sdk_root=/home/<USERNAME>/.buildozer/android/platform/android-sdk/ --install "platform-tools"
sudo ./sdkmanager --sdk_root=/home/<USERNAME>/.buildozer/android/platform/android-sdk/ --install "patcher;v4"
sudo ./sdkmanager --sdk_root=/home/<USERNAME>/.buildozer/android/platform/android-sdk/ --install "emulator"
```
