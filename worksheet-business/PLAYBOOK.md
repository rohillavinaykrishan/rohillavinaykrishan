# Roz Abhyas (रोज़ अभ्यास): daily worksheets on WhatsApp

Every morning, each subscribed parent gets one PDF on WhatsApp: a worksheet for their child's class with Maths, English and Hindi questions (about 20 minutes of work), plus an answer key for the parent.

"Roz Abhyas" is only a working name. Change it if you like.

---

## 1. Team roles

| Who | Job |
|---|---|
| **You (owner)** | Find parents, collect payments, send the PDF each morning, answer questions |
| **Claude: content writer** | Writes each day's questions for every class, matched to the CBSE / state-board syllabus |
| **Claude: checker** | Re-checks every answer before a sheet goes out |
| **Claude: designer** | Turns the questions into the branded PDF (`src/build.js`) |
| **Claude: sales manager** | Writes your messages, offers and replies |

**Your quality rule:** before sending, open the answer key and solve 2–3 questions yourself. If a parent finds one wrong answer, they lose trust. That check is your job.

---

## 2. Prices

| Plan | Price | Includes |
|---|---|---|
| **Free trial** | ₹0 | 7 days of sheets |
| **Monthly** | ₹149 for 1 child | A sheet every day from Monday to Saturday, plus a weekly revision test on Sunday |
| **Sibling** | ₹249 for 2 children | Same as monthly |
| **3 months** | ₹399 | Same as monthly, about ₹50 saved |

Payments are by UPI, in advance, every month. Don't start sending until the payment arrives.

---

## 3. How to spend the ₹1,000

| Item | Cost | Why |
|---|---|---|
| 100 printed flyers (A5, black and white) | about ₹200–300 | Hand them out outside schools at closing time and in tuition areas |
| 10 printed sample worksheets | about ₹30–50 | Parents trust paper they can hold more than a PDF |
| WhatsApp Business app | ₹0 | Gives you a catalog, an automatic welcome message and labels |
| **Reserve** | about ₹650 | Don't spend it until something works, then use it to boost a Facebook post to local parents |

---

## 4. Messages to send (copy and paste)

**For your own contacts and family groups (Hindi):**

> नमस्ते 🙏 मैंने बच्चों के लिए **रोज़ अभ्यास** शुरू किया है।
> हर सुबह WhatsApp पर आपके बच्चे की class (1 से 8) की एक worksheet आएगी, जिसमें गणित, English और हिंदी के सवाल होंगे। सिर्फ़ 20 मिनट रोज़, और साथ में answer key भी मिलेगी।
> ✅ **7 दिन बिल्कुल free**
> उसके बाद सिर्फ़ ₹149/महीना (₹5 रोज़ से भी कम)
> Sample नीचे भेज रहा हूँ 👇 बच्चे की class बताइए, कल सुबह से शुरू कर देते हैं।

**English version:**

> Hi! I've started **Roz Abhyas**: a daily practice sheet on WhatsApp for kids in Class 1–8, with Maths, English and Hindi. It takes 20 minutes a day, and an answer key comes with every sheet.
> ✅ **7 days free**, then just ₹149/month.
> Sample attached 👇 Reply with your child's class and I'll start tomorrow morning.

**On day 6 of the trial (this is when trial users turn into paying customers):**

> नमस्ते! आपके बच्चे का free trial कल ख़त्म हो रहा है। कैसा लगा? 😊
> आगे जारी रखने के लिए ₹149 इस UPI पर भेज दीजिए: ________
> Sibling plan ₹249 में 2 बच्चों के लिए है।

**Ask happy parents for referrals:**

> अगर आपको रोज़ अभ्यास पसंद आया हो, तो 2 और parents को बताइए। उनके join करने पर आपका अगला महीना ₹50 कम हो जाएगा 🙏

---

## 5. Daily routine (about 30 minutes)

1. **The night before:** ask Claude, "Make tomorrow's sheets for Class X, Y, Z, Day N." Claude writes the JSON files and builds the PDFs.
2. **Check:** solve 2–3 answers yourself.
3. **7:00 am:** send each PDF through a WhatsApp **Broadcast list** (one list per class, so parents' numbers stay private).
4. **Evening:** reply to questions and remind trial parents.

Only make sheets for the classes you actually have subscribers in. You don't need all eight on day one.

---

## 6. First 30 days

| Days | Goal |
|---|---|
| 1–3 | Send the samples to 50 contacts, get 10 parents on the free trial |
| 4–7 | Hand out flyers outside 2 schools, get 10 more trial parents |
| 8–14 | Turn trial users into paying customers: aim for 8–10 paying |
| 15–30 | Referrals and the Facebook boost: aim for 20 paying, about ₹3,000/month |

**Being honest:** usually only 3–5 out of every 10 trial parents end up paying. To get 20 paying parents, plan to give the free trial to about 50.

---

## 7. Ways to grow later

- An **exam-time pack** (₹99 one-time): 10 revision sheets before half-yearly and annual exams
- Sell **printed sheets** to small tuition teachers in bulk
- A **holiday homework helper** pack in summer and winter

## Files

- `samples/class3-day1.pdf`, `samples/class6-day1.pdf`: sample worksheets to show parents
- `src/*.json`: the questions for each sheet
- `src/build.js`: builds the PDFs (`cd src && node build.js class3-day1.json`)
