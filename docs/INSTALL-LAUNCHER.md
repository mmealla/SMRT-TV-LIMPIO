# Instalar el launcher en tu TV

Guía para construir e instalar **SMRT-TV-LIMPIO** en un televisor Android/Google TV.

## 1. Prerrequisitos

- **JDK 17** (Temurin/Adoptium recomendado)
- **Android SDK** (API 34) con `platform-tools` (para `adb`)
- **Gradle** (incluido vía `gradlew`, no hace falta instalarlo)
- Una **PC en la misma red Wi-Fi** que el televisor
- El televisor con **depuración USB/inalámbrica activada**

### Activar depuración en el TV

1. Ajustes → Preferencias del dispositivo → Acerca de
2. Presioná OK sobre **Build** 7 veces → aparece "Eres desarrollador"
3. Volvé a Ajustes → Preferencias del dispositivo → Opciones de desarrollador
4. Activá **Depuración USB** (y **Depuración inalámbrica** si aparece)
5. Aceptá el aviso "¿Permitir depuración USB?" cuando lo pida

## 2. Clonar y construir

```bash
git clone https://github.com/mmealla/SMRT-TV-LIMPIO.git
cd SMRT-TV-LIMPIO/cleanyourtv/launcher
```

### Windows (PowerShell/CMD)

```powershell
$env:GRADLE_USER_HOME = "D:\MAXI\TV\gradle-home"   # o cualquier carpeta
.\gradlew.bat assembleRelease
```

### Linux/macOS

```bash
GRADLE_USER_HOME="$HOME/.gradle" ./gradlew assembleRelease
```

El APK queda en:

```
app/build/outputs/apk/release/app-release.apk
```

> El gate de CI exige que el APK pese **≤ 440 KB**. Esta build pesa ~331 KB.

## 3. Conectar el TV por ADB

### USB (cable)

Conectá el TV por cable USB a la PC y verificá:

```bash
adb devices
```

### Inalámbrico (Wi-Fi)

En el TV: Ajustes → Opciones de desarrollador → **Depuración inalámbrica** → "Emparejar dispositivo con código de emparejamiento". Te va a mostrar:

- **IP:puerto de emparejamiento** (ej: `192.168.100.25:37123`)
- **Código de emparejamiento** (6 dígitos)

En la PC:

```bash
adb pair 192.168.100.25:37123 123456
adb connect 192.168.100.25:40425   # el puerto de conexión (distinto al de emparejamiento)
```

Verificá con `adb devices`.

## 4. Instalar el launcher

```bash
adb install -r app/build/outputs/apk/release/app-release.apk
```

El flag `-r` reinstala si ya estaba instalado. Debería decir `Success`.

## 5. Usar el launcher

### Clima
- El bloque de clima está debajo de los botones superiores (Ajustes, etc.).
- Navegá con el D-pad hasta el bloque de clima y presioná **OK**.
- Se abre un diálogo con opciones: Automático (por IP), ciudades predefinidas, o "Buscar otra ciudad".
- "Buscar otra ciudad" permite escribir el nombre y elegir entre los resultados (búsqueda async, no bloquea la UI).

### Renombrar apps
1. Activá el **modo de reordenamiento** (botón de reordenar en la barra superior).
2. Enfocá el tile de la app que querés renombrar.
3. **Mantené presionado OK ~1 segundo** → aparece un menú con "Renombrar app" e "Info de la app".
4. Elegí "Renombrar app", escribí el nombre nuevo y presioná Guardar.
5. El nombre se persiste y sobrevive reinicios. Presionar "Cancelar" descarta.

### Reordenar apps
- En modo de reordenamiento, presioná OK sobre un tile para "recogerlo", mové con las flechas, y presioná OK de nuevo para soltarlo.
- Back termina el modo y guarda el orden.

## 6. Solución de problemas

### "La pantalla se pone negra y no hace nada" al presionar el clima
- Asegurate de tener la última build (el diálogo usa `AlertDialog`, que es visible en TV).
- Si persiste, capturá el logcat: `adb logcat -d | grep -i "TvHome\|Weather"`.

### No se conecta por ADB
- Verificá que el TV y la PC estén en la misma red Wi-Fi.
- Asegurate de que la depuración inalámbrica esté activa en el TV.
- Algunos TVs requieren emparejamiento con código (ver sección 3).
- Si el puerto 5555 está cerrado, usá el puerto de conexión que muestra el TV.

### El APK no instala ("INSTALL_FAILED")
- Verificá que el APK sea el de release (`app-release.apk`).
- Si hay una versión anterior instalada con firma distinta, desinstalala primero: `adb uninstall com.gathin.tvhome`.

### El nombre de una app no cambia
- Asegurate de estar en **modo de reordenamiento** antes de mantener OK.
- El nombre debe tener al menos un carácter no vacío.
- Los nombres pasan por `Cards.cleanLabel` (se recortan espacios, se eliminan caracteres de control, máx 40 caracteres).

### La app no aparece como launcher por defecto
- Ajustes → Preferencias del dispositivo → Pantalla de inicio → seleccioná "CleanYourTV" (o "TvHome").

## 7. Verificación

Para confirmar que todo funciona:

```bash
adb devices                          # TV conectado
adb shell pm list packages | grep gathin   # paquete instalado
adb shell am start -n com.gathin.tvhome/.MainActivity   # lanzar
```

---

*Basado en el proyecto original [cleanyourtv](https://github.com/Gathin23/cleanyourtv) de @gathint, mejorado por @mmealla.*