# SUIIT Cover Page Generator

A production-ready Next.js platform that lets students generate professional
college cover pages from pre-designed Microsoft Word (`.docx`) templates —
**without editing Word manually**.

The generated DOCX preserves the template's original formatting exactly while
replacing placeholders with user-provided values. Everything runs locally in
the browser. **No AI models. No external APIs.**

---

## ✨ Features

- **Live preview** — updates instantly on every keystroke (no refresh, no loading).
- **Placeholder replacement** — Docxtemplater injects form values into the DOCX.
- **Custom template upload** — upload your own `.docx`, placeholders are detected automatically and a dynamic form is generated for each one.
- **Plain template auto-detect** — upload a `.docx` with no placeholders; editable fields are detected from labels, underlines and blank cells, then click-to-mapped and filled in place.
- **Logo insertion** — upload a PNG, JPEG or SVG; it's normalised and embedded as an inline image.
- **Font controls** — family, size, weight, alignment (style the live preview).
- **Zod validation** — required fields, inline error messages, empty downloads prevented.
- **Toast notifications + progress indicator** — clear success/error feedback.
- **Scalable template system** — add lab, assignment, seminar, internship, thesis covers without touching business logic.
- **Premium, minimal UI** — Linear/Vercel-style design system with Geist + Inter.

---

## 🚀 Getting Started

### Prerequisites

- Node.js **18.17+** (tested on v22)
- npm

### Install

```bash
npm install
```

### Run (development)

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Production build

```bash
npm run build
npm start
```

### Quality checks

```bash
npm run typecheck   # tsc --noEmit
npm run lint        # eslint
```

---

## 🧱 Tech Stack

| Area            | Technology                                   |
| --------------- | -------------------------------------------- |
| Framework       | Next.js 16 (App Router) + TypeScript         |
| Styling         | Tailwind CSS, shadcn/ui                       |
| Forms           | React Hook Form + Zod                         |
| Animation       | Framer Motion, Lucide React                   |
| DOCX generation | Docxtemplater + PizZip + File Saver           |
| DOCX preview     | docx-preview                                  |
| File upload     | React Dropzone                                |
| Toasts          | Sonner                                        |

---

## 📁 Project Structure

```
.
├── app/                  # App Router pages + root layout
│   ├── layout.tsx        # Fonts, metadata, Toaster
│   ├── page.tsx          # Landing page
│   └── generate/         # Generator page
├── components/
│   ├── ui/               # shadcn-style primitives (Button, Card, Select…)
│   ├── shared/           # Reusable FieldWrapper, FormSection, SectionHeader
│   ├── landing/          # Hero, Features, HowItWorks, Templates, FAQ, CTA
│   ├── generator/        # Generator, CustomTemplateUpload, PlainTemplateUpload, DownloadButton
│   ├── navbar.tsx
│   ├── footer.tsx
│   └── cover-preview.tsx # Live DOCX approximation
├── hooks/                # useLogo (upload + SVG→PNG normalisation)
├── lib/                  # docx generation, validation, placeholders, docx-analyzer, logo, utils
├── types/                # Shared TypeScript types
├── constants/            # Templates registry, fonts, sizes
├── scripts/              # Template build tooling
├── public/templates/     # DOCX templates + preview images
└── styles/               # Global styles
```

---

## 📄 DOCX Template System

Templates live in `public/templates/` (e.g. `cover-template.docx`). Each
template is a normal `.docx` containing placeholders:

```
{{COLLEGE_NAME}}  {{INSTITUTE_NAME}}  {{DEPARTMENT}}
{{SUBJECT}}       {{SEMESTER}}        {{SUBMITTED_TO}}
{{SUBMITTED_BY}}  {{ACADEMIC_YEAR}}   {{DATE}}
{{NAME}}          {{ROLL_NO}}         {{SECTION}}
{{BRANCH}}        {{REGISTRATION_NO}} {{EMAIL}}
{{PHONE}}         {{LOGO}}
```

Docxtemplater replaces the text placeholders and **inherits the formatting from
the placeholders** — fonts, spacing and layout are never overwritten. The
`{{LOGO}}` placeholder is replaced with an inline image during post-processing.

### Adding a new template

Register it in `constants/index.ts` — no business logic changes required:

```ts
{
  id: "lab-cover",
  name: "Lab Cover",
  description: "A cover page for laboratory reports.",
  previewImage: "/templates/lab-cover.svg",
  docxPath: "/templates/lab-cover.docx",
  supportedPlaceholders: [ /* … */ ],
}
```

> To author a template without Word, you can extend `scripts/build-template.mjs`
> (it builds a valid OOXML package programmatically) and run
> `node scripts/build-template.mjs`.

---

## 🧩 Custom Template Upload

In addition to the predefined cover, you can **upload your own `.docx`
template** and fill it in without editing Word manually. From the *Generate*
page, switch to the **Upload Your Own** tab.

### How it works

1. **Upload** — drag & drop any `.docx` file (it never leaves your browser).
2. **Analyze** — the system detects every `{{PLACEHOLDER}}` tag using
   docxtemplater's lexer, including tags split across Word runs and tags in
   tables, headers and footers.
3. **Fill** — a form is generated dynamically with one field per placeholder.
   Placeholder names become human-readable labels (`ROLL_NO` → *Roll No*).
   Placeholders that look like images (`LOGO`, `SIGNATURE`, `SEAL`, …) render
   as image-upload controls instead of text inputs.
4. **Preview** — a real-time, near-exact render of your document (via
   docx-preview) updates as you type.
5. **Download** — the original template is filled in with Docxtemplater,
   preserving its exact formatting, layout, fonts, spacing, tables, headers,
   footers, images and styles.

### Placeholder conventions

- Text tags: `{{NAME}}`, `{{ROLL_NO}}`, `{{COLLEGE_NAME}}`, `{{ADMISSION_YEAR}}`, …
- Image tags (auto-detected, rendered as uploads): any name containing
  `LOGO`, `IMAGE`, `SIGN`, `SIGNATURE`, `SEAL`, `STAMP`, `PHOTO` or `PICTURE`.

### Backward compatibility

The predefined-template workflow is unchanged. Both modes share the same
document-generation pipeline (`lib/docx.ts` → `renderTemplateDocx`) and
reuse the existing form primitives, logo upload and download controls.

### Where the code lives

| Concern                 | Location                                                |
| ----------------------- | ------------------------------------------------------- |
| Placeholder detection   | `lib/placeholders.ts` (`extractPlaceholders`)           |
| Custom generation       | `lib/docx.ts` (`renderTemplateDocx`)                    |
| Upload + dynamic form   | `components/generator/custom-template-upload.tsx`       |
| Live DOCX preview       | `components/generator/custom-preview.tsx`               |
| Mode toggle             | `components/generator/generate-view.tsx`                |

---

## 🧩 Plain Template Upload (Auto-Detect)

Many `.docx` forms don't contain `{{PLACEHOLDERS}}` — they're just a Word page
with **labels** (`Name:`, `Roll No:`, `Subject:`), **underlines**, and empty
**table cells**. The **Plain Template** tab handles these without any manual
placeholder editing.

### How it works

1. **Upload** — drag & drop any plain `.docx` (it never leaves your browser).
2. **Auto-detect** — `lib/docx-analyzer.ts` parses the document body and flags
   likely editable regions using deterministic rules:
   - label lines (e.g. `Name : ___` → the trailing space/underline is the field),
   - a label paragraph followed by a blank or underlined line,
   - blank table cells immediately after a label cell,
   - standalone underline-only lines (e.g. signature lines).
3. **Click-to-map** — a mapping list shows every paragraph and table cell.
   Auto-detected fields are pre-selected; click any region to add or remove it
   as an editable field, and rename each field's label.
4. **Fill** — a dynamic form renders one input per mapped field.
5. **Preview** — a real-time, near-exact render updates as you type.
6. **Download** — the mapped regions are converted to placeholders and filled
   through the same Docxtemplater pipeline as everything else.

### How it preserves formatting

Detection never edits the file. Instead, `applyFieldAssignments` rewrites only
the assigned paragraphs/cells by injecting a `{{FIELD_n}}` placeholder into a
run that reuses the region's original run/paragraph/cell properties (keeping
the label prefix for `tail` mode). Everything else — text, fonts, spacing,
tables, images, headers, footers, styles — is left byte-for-byte untouched,
and the result flows through the shared `renderTemplateDocx`.

### Where the code lives

| Concern                | Location                                         |
| ---------------------- | ------------------------------------------------ |
| Document analysis      | `lib/docx-analyzer.ts` (`analyzeDocument`)       |
| Region injection       | `lib/docx-analyzer.ts` (`applyFieldAssignments`) |
| Upload + mapping editor| `components/generator/plain-template-upload.tsx` |

---

## 🎨 Design System

- **Background** `#FAFAFA` · **Cards** white · **Primary** `#111111`
- **Secondary** `#6B7280` · **Border** `#E5E7EB` · **Accent** `#2563EB`
- **Success** `#16A34A` · **Error** `#DC2626`
- Headings: Geist · Body: Inter · No gradients, solid colors, generous spacing.

---

## 🔒 Privacy

All processing happens client-side. Your data and uploaded files never leave
the browser.

---

## 📝 License

MIT — built for students, by students.
