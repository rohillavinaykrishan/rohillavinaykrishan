# Daily Dose: ICSE practice sheets on WhatsApp

Every morning, each subscribed parent gets one PDF on WhatsApp: a worksheet for their child's ICSE class (1–8) with Maths, English and Hindi questions (about 20 minutes of work), plus an answer key for the parent.

- **Name:** Daily Dose (change it in `src/brand.json`)
- **WhatsApp:** 82908 29427
- **Every sheet says:** "Independent practice material. Not affiliated with CISCE." (CISCE is the body that runs ICSE.) Never use the ICSE or CISCE logo.

---

## 1. Team roles

| Who | Job |
|---|---|
| **You (owner)** | Find parents, collect payments, send the PDF each morning, answer questions |
| **Claude: content writer** | Writes each day's questions at ICSE level (Selina-style Maths, grammar-heavy English, Hindi as second language) |
| **Claude: checker** | Re-checks every answer before a sheet goes out |
| **Claude: designer** | Builds the branded PDF (`src/build.js`) |
| **Claude: sales manager** | Writes your messages, offers and replies |

**Your quality rule:** before sending, solve 2–3 questions from the answer key yourself. ICSE parents check carefully, and one wrong answer loses their trust.

**Ask each new parent two things:**
1. Their child's school, and the chapter the class is on right now. Then the sheets follow what the class is actually studying.
2. Their child's second language. Most ICSE schools teach Hindi, but some teach Bengali, Marathi, Sanskrit or another language. If it isn't Hindi, the Hindi section can be swapped for extra English or Maths.

---

## 2. Prices

ICSE parents usually spend more on their children's education, so the prices are a little higher than in the first plan.

| Plan | Price | Includes |
|---|---|---|
| **Free trial** | ₹0 | 7 days of sheets |
| **Monthly** | ₹199 for 1 child | A sheet every day from Monday to Saturday, plus a revision test on Sunday |
| **Sibling** | ₹349 for 2 children | Same as monthly |
| **3 months** | ₹549 | Same as monthly, about ₹50 saved |
| **Exam pack** (later) | ₹149 one-time | 10 revision sheets before unit tests, half-yearly and annual exams |

Payments are by UPI, in advance, every month. Don't start sending until the payment arrives.

**Target:** 20 paying parents at ₹199 is about **₹4,000 a month**.

---

## 3. Where to find ICSE parents

1. **Outside ICSE schools at closing time.** Parents wait at the gate, so hand them a flyer with the sample sheet.
2. **Apartment and society WhatsApp groups.** ICSE families often live in the same societies.
3. **Small tuition teachers.** Offer them the sheets in bulk, or ₹50 for each parent they send you.
4. **Your own contacts.** Ask "Which of your friends' kids go to an ICSE school?"

---

## 4. How to spend the ₹1,000

| Item | Cost | Why |
|---|---|---|
| 100 printed flyers (A5) | about ₹200–300 | For the school gates |
| 10 printed sample worksheets (colour) | about ₹100 | Parents trust paper they can hold |
| WhatsApp Business app | ₹0 | Gives you a catalog, an automatic welcome message and labels |
| **Reserve** | about ₹600 | Don't spend it until something works, then use it to boost a Facebook post to parents near ICSE schools |

---

## 5. Messages to send (copy and paste)

ICSE parents usually prefer English, so send the English version first.

**First message (English):**

> Hi! 👋 I've started **Daily Dose**: a daily practice sheet on WhatsApp for **ICSE students in Class 1–8**.
> 📘 Maths + English + Hindi, about 20 minutes a day
> ✅ Answer key for parents with every sheet
> ✅ Matched to what your child is studying in class
> 🎁 **7 days free**, then just ₹199/month (less than ₹7 a day)
> Sample sheet attached 👇 Reply with your child's **class and school**, and I'll start from tomorrow morning.
> 📱 82908 29427

**Hindi version (for family groups):**

> नमस्ते 🙏 मैंने **ICSE बच्चों (Class 1–8)** के लिए **Daily Dose** शुरू किया है।
> हर सुबह WhatsApp पर गणित, English और हिंदी की एक worksheet आएगी, साथ में parents के लिए answer key भी।
> 🎁 **7 दिन free**, फिर सिर्फ़ ₹199/महीना।
> Sample नीचे है 👇 बच्चे की class और school बताइए।

**On day 6 of the trial:**

> Hi! Your child's free trial ends tomorrow. How did they find the sheets? 😊
> To continue, please send ₹199 to UPI: ________ (sibling plan: ₹349 for 2 children).

**Asking for referrals:**

> If Daily Dose is helping, please share it with 2 parents from your child's class. When they join, you get ₹50 off your next month 🙏

---

## 6. Daily routine (about 30 minutes)

1. **The night before:** ask Claude, "Make tomorrow's Daily Dose sheets for Class X, Y, Z, Day N. Topics: …" Claude writes the JSON files and builds the PDFs.
2. **Check:** solve 2–3 answers yourself.
3. **7:00 am:** send each PDF through a WhatsApp **Broadcast list** (one list per class, so parents' numbers stay private).
4. **Evening:** reply to questions and remind trial parents.

---

## 7. First 30 days

| Days | Goal |
|---|---|
| 1–3 | Send the samples to 50 contacts and society groups, get 10 parents on the free trial |
| 4–7 | Hand out flyers outside 2 ICSE schools, get 15 more trial parents |
| 8–14 | Turn trial users into paying customers: aim for 8–10 paying |
| 15–30 | Referrals, tuition teachers and the Facebook boost: aim for 20 paying, about ₹4,000/month |

**Being honest:** usually only 3–5 out of every 10 trial parents end up paying, so plan to give the free trial to about 50.

---

## Files

- `samples/class1-day1.pdf` … `samples/class8-day1.pdf`: Day 1 sample sheets for every class
- `src/brand.json`: name, tagline, WhatsApp number and disclaimer
- `src/classN-dayM.json`: the questions for each sheet
- `src/build.js`: builds the PDFs (`cd src && node build.js class3-day1.json`)
