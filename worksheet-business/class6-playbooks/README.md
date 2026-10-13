# ICSE Class 6: Play & Learn Playbooks

There are eight subject playbooks, each covering the whole book, made for a teacher in Mumbai to use with ICSE Class 6 students preparing for the final exam. Marathi is the students' second language.

| Subject | PDF | Notes source |
|---|---|---|
| Mathematics | `pdf/maths.pdf` | `notes/maths.md` |
| Physics | `pdf/physics.pdf` | `notes/physics.md` |
| Chemistry | `pdf/chemistry.pdf` | `notes/chemistry.md` |
| Biology | `pdf/biology.pdf` | `notes/biology.md` |
| History & Civics | `pdf/history-civics.pdf` | `notes/history-civics.md` |
| Geography | `pdf/geography.pdf` | `notes/geography.md` |
| English (Language + Literature toolkit) | `pdf/english.pdf` | `notes/english.md` |
| Marathi (Second Language) | `pdf/marathi.pdf` | `notes/marathi.md` |

## What every chapter has

- Short notes, with tables for quick revision
- 🧠 **Memory Trick:** a mnemonic, story or rhyme
- 🎲 **Play It in Class:** a 5–10 minute game or activity using simple things
- 📍 **Mumbai Connection:** local examples (BMC, local trains, Kanheri Caves, mangroves, Mumbai High…)
- ⭐ **Exam Tip** and ✏️ **Quick Check**, with the answers at the end of the book
- A **Full-Book Revision Test** at the end of each subject

## Suggested teaching plan up to the final exam

1. **Each week:** teach or revise 1–2 chapters per subject, using the game to start the class and the quick check to end it.
2. **Every Saturday:** a mixed quick-check quiz across subjects.
3. **The last 3–4 weeks before the exam:** the full-book revision tests, one subject a day.

## Please check before printing

- **Chapter names and order** differ between schools and publishers (Selina, Frank, Morning Star…). Match them to the school's **final-exam syllabus circular**.
- **English Literature and the Marathi textbook** differ from school to school. Each playbook has a toolkit (Story, Poem and Lesson cards). Share the textbook's lesson and poem names, and chapter-wise notes can be added.
- Independent study material, not affiliated with CISCE.

## Rebuilding the PDFs after editing

```
npm install            # first time only
node build-notes.js            # all subjects
node build-notes.js maths      # one subject
```
