# HaulLoop Logistics Marketplace - Frontend Android Application

HaulLoop is a high-fidelity, premium frontend Flutter application designed to connect transporters returning empty (backhauling) with business shippers needing cargo carriage. This project is 100% frontend only, featuring reactive mock models, local state synchronization via Riverpod, customizable vector tracking maps, and dual light/dark modes.

---

## 20-Point Setup, Run, and Scaling Guide

### 1. Required Software
To build and run this application, you must install the following software packages:
- **Operating System**: Windows 10/11, macOS, or Linux.
- **Git**: For version control management.
- **Flutter SDK**: The framework engine.
- **Java Development Kit (JDK)**: JDK 17 (recommended for Gradle build compilation).
- **Android Studio**: IDE containing SDK configurations.
- **VS Code** (Optional): A lightweight code editing alternative.

---

### 2. Flutter Installation
1. Download the latest stable Flutter SDK zip file for your OS from the official website ([docs.flutter.dev](https://docs.flutter.dev/get-started/install)).
2. Extract the zip file and place it in a local directory (e.g., `C:\src\flutter` on Windows; do **not** place it in `Program Files`).
3. Add the `flutter/bin` subdirectory to your system's environmental `Path` variable.
4. Open a new terminal and run `flutter --version` to check that the installation succeeded.

---

### 3. Android Studio Installation
1. Download Android Studio from [developer.android.com/studio](https://developer.android.com/studio).
2. Run the installer and proceed with the standard setup wizard.
3. Choose the **Standard** setup type to download essential components, including the Android Emulator.
4. During installation, select your preferred UI theme (Light or Dark).

---

### 4. VS Code Installation
1. Download and install VS Code from [code.visualstudio.com](https://code.visualstudio.com).
2. Open VS Code, navigate to the Extensions tab (`Ctrl+Shift+X`).
3. Search for and install the **Flutter** extension (published by `Dart Code`). This automatically installs the **Dart** extension.

---

### 5. Android SDK Setup
1. Launch Android Studio.
2. Go to **Settings** / **Preferences** -> **Appearance & Behavior** -> **System Settings** -> **Android SDK**.
3. Under the **SDK Platforms** tab, check the box for the latest Android API level (e.g., Android 13 or 14).
4. Under the **SDK Tools** tab, verify that these options are checked:
   - Android SDK Build-Tools
   - Android Emulator
   - Android SDK Platform-Tools
   - Android SDK Command-line Tools (latest)
5. Click **Apply** to download and install.

---

### 6. Environment Variables (Windows)
1. In the Windows Search bar, type `env` and select **Edit the system environment variables**.
2. Click **Environment Variables** at the bottom.
3. Under **User Variables** or **System Variables**, click **New** to add `ANDROID_HOME`:
   - Variable Name: `ANDROID_HOME`
   - Variable Value: `C:\Users\<Your-Username>\AppData\Local\Android\Sdk`
4. Find the `Path` variable, select **Edit**, click **New**, and append these directories:
   - `%ANDROID_HOME%\platform-tools`
   - `%ANDROID_HOME%\tools`
   - `C:\src\flutter\bin` (if not done in Step 2)
5. Save changes and restart your terminal to apply the updates.

---

### 7. Emulator Creation (AVD Manager)
1. Open Android Studio.
2. From the welcome window or menu, choose **Device Manager** (found in the top right or under "More Actions").
3. Click **Create Device**.
4. Select a phone model (e.g., **Pixel 6** or **Pixel 7 Pro**).
5. Choose a system image (e.g., **API 33** or **API 34**). Download it if necessary.
6. Click **Next**, review configurations, select **Portrait** orientation, and click **Finish**.
7. Click the green **Play** button next to your new device in the Device Manager to launch the emulator.

---

### 8. Running on Emulator
1. Start your emulator via the AVD Manager.
2. Navigate to your project directory in your terminal:
   ```powershell
   cd c:\Users\manas\Downloads\backhaul
   ```
3. Run `flutter devices` to ensure the running emulator is recognized.
4. Run the application:
   ```powershell
   flutter run
   ```

---

### 9. Running on Physical Android Phone
1. Connect your Android phone to your PC via a USB cable.
2. On your phone, go to **Settings** -> **About Phone** -> Tap **Build Number** 7 times to enable Developer Mode.
3. Go to **Settings** -> **Developer Options** and toggle on **USB Debugging**.
4. Select **Always allow from this computer** when prompted on your phone screen.
5. In your PC terminal, verify your device appears:
   ```powershell
   flutter devices
   ```
6. Run `flutter run` and select your physical device from the options.

---

### 10. USB Debugging Details
If your device is connected but unrecognized:
- Verify the USB connection mode is set to **MTP (File Transfer)** instead of "Charging only".
- Ensure the appropriate OEM USB drivers are installed (especially for Samsung/Xiaomi on Windows). Download them from the vendor website.
- Try running `adb kill-server` followed by `adb start-server` in the terminal to restart the adb daemon.

---

### 11. Wireless Debugging (Android 11+)
1. Ensure both your computer and your phone are connected to the same Wi-Fi network.
2. Connect your phone via USB first, then enable **Wireless Debugging** in Developer Options.
3. In your terminal, run:
   ```powershell
   adb tcpip 5555
   ```
4. Find your phone's IP address (visible in Wireless Debugging settings, e.g. `192.168.1.50`).
5. Disconnect the USB cable. Run:
   ```powershell
   adb connect 192.168.1.50:5555
   ```
6. Run `flutter devices` to verify the wireless link, then deploy using `flutter run`.

---

### 12. Flutter Doctor Fixes
Run `flutter doctor` in your terminal to diagnose system issues. Common warning fixes include:
- **Android toolchain issues / licenses not accepted**: Run `flutter doctor --android-licenses` and accept all prompts (`y`).
- **Android Studio not found**: Run:
   ```powershell
   flutter config --android-studio-dir="C:\Program Files\Android\Android Studio"
   ```
- **Visual Studio / desktop toolchain missing**: You can ignore this if you are targetting Android mobile devices exclusively.

---

### 13. How to Install Dependencies
Run this command from the root of the project to download all packages specified in the `pubspec.yaml` file:
```powershell
flutter pub get
```

---

### 14. How to Run the Project
Ensure a simulator or physical phone is running, then run:
```powershell
flutter run
```
To run in release mode (for maximum performance and smooth transitions):
```powershell
flutter run --release
```

---

### 15. How to Build Debug APK
To compile a debug binary for test sharing:
```powershell
flutter build apk --debug
```
The compiled output is located at:
`build/app/outputs/flutter-apk/app-debug.apk`

---

### 16. How to Build Release APK
To compile an optimized production binary:
```powershell
flutter build apk --release
```
The compiled output is located at:
`build/app/outputs/flutter-apk/app-release.apk`

---

### 17. Folder Structure Explanation
This project follows **Clean Architecture** patterns under the `lib/` directory:
- `core/`: Common tools that span multiple features.
  - `constants/`: Global assets and styling tokens (colors).
  - `theme/`: Material 3 Light/Dark configuration presets.
  - `routes/`: Routing and transitions configured via `go_router`.
  - `models/`: Blueprint schemas (User, Truck, Load, Booking, Transaction).
  - `widgets/`: Reusable custom UI controls (custom buttons, glassmorphic cards, simulated map painter).
  - `providers/`: Centralized mock repositories managing reactive states via `flutter_riverpod`.
- `features/`: Individual product features, each containing screen layout files.
  - `splash/`: Initial animations and redirections.
  - `onboarding/`: 3-slide value-proposition tutorial screens.
  - `auth/`: Login OTP forms and role selectors.
  - `home/`: Role-specific dashboard layouts (Shipper, Transporter, Admin).
  - `marketplace/`: Search lists and AI score analysis pages.
  - `booking/`: Step-by-step booking payment forms and completion panels.
  - `tracking/`: Map paint feeds, progress timelines, and live GPS simulator sliders.
  - `wallet/`: Escrow logs, transaction items, and invoice detail panels.
  - `notifications/`: System alert groups.
  - `profile/`: Account specifications, settings, and GST/KYC compliance logs.

---

### 18. How to Replace Dummy Data with APIs Later
To move from local simulated databases to live REST/GraphQL APIs:
1. Create a `data/` subdirectory inside each feature folder to handle networking logic (e.g. `data/repositories/` and `data/datasources/`).
2. Integrate the `http` or `dio` package in your `pubspec.yaml`.
3. In `global_providers.dart`, replace StateNotifiers containing hardcoded lists with async providers (e.g., `FutureProvider` or `AsyncNotifierProvider`). For example:
   ```dart
   final loadsProvider = AsyncNotifierProvider<LoadsNotifier, List<Load>>(() => LiveLoadsNotifier());
   ```
4. Fetch remote data in these providers using async network requests and map the JSON responses to your existing models using serialization methods (`fromJson` and `toJson`).

---

### 19. Where to Connect Backend Later
API connection points are isolated in the providers file:
- **Authentication**: Modify the `authProvider` in `lib/core/providers/global_providers.dart` to make a POST request containing credentials to `/api/auth/login` and store the returned JWT token.
- **Loads**: Modify the `loadsProvider` to make requests to `/api/loads` (GET to fetch list, POST to create a new load).
- **Trucks**: Connect the `trucksProvider` to `/api/trucks` to retrieve carrier fleets or register a new truck.
- **Bookings**: Connect the `bookingsProvider` to `/api/bookings` (POST to allocate escrow, PUT to push GPS progress updates).

---

### 20. Best Practices for Scaling to Production
To expand this project into a secure, production-grade logistics application:
1. **Secure Storage**: Save user authentication tokens and sensitive settings using the `flutter_secure_storage` package.
2. **State Caching**: Integrate a local database cache (such as `Hive` or `Isar`) to support offline capabilities, letting transporters access trip schedules and route guidelines in remote areas without internet connections.
3. **WebSockets**: Replace the manual GPS simulator slider with real-time WebSocket listeners (`web_socket_channel`) to pull live GPS coordinates from drivers and move the truck on the map automatically.
4. **Error Handling**: Implement custom error handlers and retry policies (e.g., using `Fuzzy Exponential Backoff`) for network connections.
5. **Crash Analytics**: Integrate tracking SDKs like `Firebase Crashlytics` or `Sentry` to monitor crashes and application performance in production.
