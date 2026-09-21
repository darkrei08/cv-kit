# Cross-platform notes

The pipeline has one genuinely platform-specific step: producing a PDF from a
`.docx`. Everything else — reading the data, building the document, checking the
result — is pure Python and behaves identically everywhere.

## What each system needs

### Building documents (all systems)

```bash
python -m pip install -e .
```

Requires Python 3.10 or newer, `python-docx` and `pillow`. Nothing else.

### Quality checks (all systems)

```bash
python -m pip install -e ".[qa]"
```

Adds PyMuPDF, which is what measures page counts, the text layer and the printable
area. Without it the checks that need a rendered page are reported as skipped — never
as passed.

### PDF export, best fidelity

| System | Backend | What to install |
|---|---|---|
| Windows | `word` (Word through COM, driven by PowerShell) | Microsoft Office |
| Windows / macOS | `docx2pdf` | `pip install "cvkit[pdf]"` and Microsoft Word |
| all | `libreoffice` | see below |

`cvkit build` probes the backends in that order and uses the first one that works.
`cvkit doctor` prints which ones this machine has. On Linux, LibreOffice is the
supported PDF backend; Word and `docx2pdf` are not expected to work there.

If a native Linux package is not available, the Flatpak build is a supported
alternative:

```bash
flatpak install flathub org.libreoffice.LibreOffice
```

Expose `flatpak run org.libreoffice.LibreOffice` as a `soffice` command on `PATH`
so `cvkit` can discover it. Keep the output PDF under the project or home directory,
not `/tmp`: the exporter creates LibreOffice's temporary conversion directory beside
the destination PDF so the Flatpak can access it.

### PDF export, without any office suite

```bash
# Debian, Ubuntu, Mint, Pop!_OS, Kali
sudo apt update && sudo apt install libreoffice-writer

# Fedora, RHEL, CentOS Stream, Rocky, AlmaLinux
sudo dnf install libreoffice-writer

# Arch, Manjaro, EndeavourOS, Garuda
sudo pacman -S libreoffice-fresh

# openSUSE
sudo zypper install libreoffice-writer

# Alpine
apk add libreoffice

# macOS (Homebrew)
brew install --cask libreoffice

# Windows
winget install TheDocumentFoundation.LibreOffice
choco install libreoffice-fresh
```

LibreOffice pagination is very close to Word's but not guaranteed identical. That is
why the quality checks re-measure the produced PDF instead of trusting the source
document: `cvkit qa` reports the actual page count per file whatever engine produced
it.

### Plain-text export for web forms

```bash
# macOS
brew install pandoc
# Debian / Ubuntu
sudo apt install pandoc
# Fedora
sudo dnf install pandoc
# Arch
sudo pacman -S pandoc
# Windows
winget install JohnMacFarlane.Pandoc
```

Pandoc is optional: without it, `cvkit` falls back to a built-in extractor that reads
paragraphs and table cells with `python-docx`. The output is slightly plainer and
still correct.

### The HTML variant

```bash
python -m pip install -e ".[html]"
```

WeasyPrint needs system libraries on Linux:

```bash
# Debian / Ubuntu
sudo apt install libpango-1.0-0 libpangoft2-1.0-0 libcairo2
# Fedora
sudo dnf install pango cairo
# Arch
sudo pacman -S pango cairo
# macOS
brew install pango libffi
```

### Timeline diagrams

```bash
npm install -g @mermaid-js/mermaid-cli
npx -y puppeteer browsers install chrome   # if no browser is installed
```

Mermaid CLI drives a headless browser. On a machine with no Chromium-family browser
(a bare Windows server, for instance), `npx puppeteer browsers install chrome`
downloads one into the user cache; `cvkit diagram` writes the Puppeteer configuration
file it needs and finds the browser automatically.

## Paths

Two details that bite on Windows and are handled in the code:

- **Mermaid configuration.** JSON does not accept unescaped backslashes, so a
  `C:\...\chrome.exe` path written naively makes Mermaid CLI fail with a JSON error.
  `cvkit.diagrams.write_puppeteer_config` writes forward slashes, which Node accepts
  on every system.
- **`/tmp` in a Unix shell on Windows.** Git Bash turns `/tmp/x` into `C:\tmp\x`. Tools
  that resolve paths themselves, like `anydoc`, then fail. Pass project-relative or
  explicit Windows paths instead.

## Fonts

The ATS variant uses Arial and the designed variant uses Calibri with Georgia for
headings. Word has all three. LibreOffice substitutes them if they are absent:

```bash
# Debian / Ubuntu
sudo apt install ttf-mscorefonts-installer fonts-liberation
# Fedora
sudo dnf install mscorefonts liberation-sans
# macOS
brew install --cask font-arial font-calibri
```

Liberation Sans is metric-compatible with Arial, so pagination barely moves. If a
document must look identical on a machine without Microsoft fonts, install them, or
accept the substitution — the quality checks will tell you if the page count changed.

## Continuous integration

`.github/workflows/ci.yml` runs two jobs:

- **test**: unit tests and a document-only build on Ubuntu, macOS and Windows across
  Python 3.10 to 3.13. No office suite, so it is fast and always runs.
- **office**: installs LibreOffice on all three systems and runs the full pipeline,
  including the page-count checks, then uploads the produced files as artifacts. This
  is the job that proves the cross-platform claim.

Word cannot be installed on a hosted runner, so the Word backend is exercised only on
a developer machine. The LibreOffice backend is the portable one and is what CI
verifies on every system.
