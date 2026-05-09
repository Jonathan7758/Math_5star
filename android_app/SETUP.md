# After Flutter SDK is installed, run these commands:

# 1. Verify installation
flutter doctor -v

# 2. Create Android project structure (run from C:\projects\Math-5star)
flutter create --org com.math5star --project-name math_5star --platforms=android android_app

# 3. Restore our custom lib/ code
# (flutter create will generate a default lib/, but our code is already there)
# Just confirm: git status should show our custom files

# 4. Install dependencies
cd android_app
flutter pub get

# 5. Build APK
flutter build apk --release
# APK will be at: build/app/outputs/flutter-apk/app-release.apk

# 6. Or run on connected device/emulator
flutter run
