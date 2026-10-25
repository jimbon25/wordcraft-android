# WordCraft for Android

Standalone offline Android APK installer for **WordCraft** (`storytold/wordcraft`), the modern, clean-room open-source reimplementation of Microsoft Word written in pure Rust.

Designed specifically for Android tablets and large screen devices like the **Xiaomi Pad 7** (11.2", 3.2K display, keyboard dock support).

---

## Highlights

- **100% Offline Standalone APK:** Bundles WordCraft's WebAssembly engine and assets directly inside the APK. No internet connection required.
- **Desktop Microsoft Word Experience:** Full desktop ribbon UI, live style previews, tables, footnotes, APA/MLA citations, mail merge, and dark mode.
- **DOCX / Document Fidelity:** Reads and writes `.docx` (OOXML), `.odt`, `.rtf`, `.md`, and exports directly to vector PDF.
- **Hardware Acceleration:** Native WebGL2/WebGPU rendering on Android at 120Hz/144Hz.
- **Physical Keyboard & Shortcut Support:** Seamlessly supports Xiaomi Pad 7 keyboard dock with shortcuts like `Ctrl+B`, `Ctrl+S`, `Ctrl+Z`, `Ctrl+C`, `Ctrl+V`, `F7`.
- **Integrated Android Storage:** Saves documents directly to `Downloads/WordCraft/` and opens existing files using the native Android document picker.

---

## Installation

1. Download the latest `WordCraft-v0.10.0-android.apk` from [GitHub Releases](https://github.com/jimbon25/wordcraft-android/releases) or the latest Actions Artifact.
2. Install the APK on your Android tablet or phone.
3. Open **WordCraft** and start writing!

---

## Automated CI / CD

The entire build pipeline is executed automatically on **GitHub Actions (`ubuntu-latest`)**:
- Bundles official upstream WebAssembly assets from [storytold/wordcraft](https://github.com/storytold/wordcraft).
- Packages Android assets with secure `WebViewAssetLoader` and MIME streaming for `.wasm`.
- Builds and signs the release APK with Android Gradle.
- Publishes artifacts and GitHub Releases.
