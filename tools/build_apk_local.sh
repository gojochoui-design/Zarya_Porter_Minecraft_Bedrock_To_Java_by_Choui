#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$SCRIPT_DIR/.."
BUILD_ROOT="${ZARYA_APK_ROOT:-$HOME/zarya-apk-build}"
ANDROID_SRC="$SRC/android"

echo "== Zarya Porter by Choui - one-command local APK build =="
echo "== Build workspace: $BUILD_ROOT (needs ~8 GB free; path must not contain spaces) =="

command -v python3 >/dev/null || { echo "python3 required"; exit 1; }
python3 -m pip install --quiet buildozer cython cmake || true

mkdir -p "$BUILD_ROOT"
cd "$BUILD_ROOT"

if [ ! -d jdk ]; then
  echo "== Fetching JDK 17 =="
  curl -sL --retry 5 -o jdk.tar.gz "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.13%2B11/OpenJDK17U-jdk_x64_linux_hotspot_17.0.13_11.tar.gz"
  mkdir -p jdk && tar xzf jdk.tar.gz -C jdk --strip-components=1 && rm jdk.tar.gz
fi
export JAVA_HOME="$BUILD_ROOT/jdk"
export PATH="$JAVA_HOME/bin:$PATH"

if [ ! -d sdk/cmdline-tools/latest/bin ]; then
  echo "== Fetching Android SDK command-line tools =="
  curl -sL --retry 5 -o ctools.zip "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip"
  mkdir -p sdk/cmdline-tools && unzip -q ctools.zip -d sdk/cmdline-tools-tmp
  mv sdk/cmdline-tools-tmp/* sdk/cmdline-tools/latest && rmdir sdk/cmdline-tools-tmp
  rm ctools.zip
fi
export ANDROIDSDK="$BUILD_ROOT/sdk"
export PATH="$ANDROIDSDK/cmdline-tools/latest/bin:$PATH"
yes | sdkmanager --licenses >/dev/null 2>&1 || true
sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0" >/dev/null
mkdir -p "$ANDROIDSDK/tools/bin"
printf '#!/bin/bash\nexec %s/cmdline-tools/latest/bin/sdkmanager "$@"\n' "$ANDROIDSDK" > "$ANDROIDSDK/tools/bin/sdkmanager"
chmod +x "$ANDROIDSDK/tools/bin/sdkmanager"

if [ ! -d ndk ]; then
  echo "== Fetching Android NDK r28c (large) =="
  curl -sL --retry 5 -o ndk.zip "https://dl.google.com/android/repository/android-ndk-r28c-linux.zip"
  unzip -q ndk.zip -d "$BUILD_ROOT" && rm ndk.zip
  mv "$BUILD_ROOT/android-ndk-r28c" "$BUILD_ROOT/ndk"
fi
export ANDROIDNDK="$BUILD_ROOT/ndk"
mkdir -p "$HOME/.buildozer/android/platform"
ln -sfn "$ANDROIDNDK" "$HOME/.buildozer/android/platform/android-ndk-r28c"

if ! command -v libtoolize >/dev/null; then
  echo "== Building libtool to ~/.local =="
  curl -sL --retry 5 -o libtool.tar.xz "https://mirrors.kernel.org/gnu/libtool/libtool-2.5.4.tar.xz"
  tar xJf libtool.tar.xz && cd libtool-2.5.4
  ./configure --prefix="$HOME/.local" >/dev/null && make -j"$(nproc)" >/dev/null && make install >/dev/null
  cd "$BUILD_ROOT" && rm -rf libtool-2.5.4 libtool.tar.xz
fi
export PATH="$HOME/.local/bin:$PATH"
export ACLOCAL_PATH="$HOME/.local/share/aclocal"

echo "== Mirroring app sources to a space-free build dir =="
rm -rf "$BUILD_ROOT/app"
mkdir -p "$BUILD_ROOT/app"
rsync -a --exclude '.buildozer' --exclude '__pycache__' "$ANDROID_SRC/" "$BUILD_ROOT/app/"
cp "$SCRIPT_DIR/patch_p4a.py" "$BUILD_ROOT/app/"
cd "$BUILD_ROOT/app"

echo "== Buildozer first pass (clones python-for-android) =="
buildozer android debug || true
python3 "$BUILD_ROOT/app/patch_p4a.py" "$BUILD_ROOT/app/.buildozer/android/platform/python-for-android"

echo "== Pre-caching freetype from a working mirror =="
FT_CACHE="$BUILD_ROOT/app/.buildozer/android/platform/build-arm64-v8a/packages/freetype"
mkdir -p "$FT_CACHE"
if [ ! -f "$FT_CACHE/freetype-2.14.1.tar.gz" ]; then
  curl -sL --retry 5 -o "$FT_CACHE/freetype-2.14.1.tar.gz" \
    "https://mirror.netcologne.de/savannah/freetype/freetype-2.14.1.tar.gz"
fi
touch "$FT_CACHE/.mark-freetype-2.14.1.tar.gz"

echo "== Final buildozer pass (compiles python + kivy + packs the APK) =="
buildozer android debug

echo "== APK ready =="
ls -la "$BUILD_ROOT/app/bin/"*.apk
echo "Copy it to your phone, enable 'install unknown apps', install. Done."
