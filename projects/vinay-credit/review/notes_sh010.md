# sh010 - VFX Supervisor review - deliver/Vinay_Krishan_Rohilla_StreetFighter_SrMatchmove_v3_4K.mp4

NOTES:

Tech is clean: 2160x3840, 25 fps, 375 frames, 15.00 s, AAC. 0 frames with mean B > R (max B-R = -25), roll type is
razor-sharp at 100%, and the roll is readable at phone size (checked at 405 px wide). Layers read: the plate is
clearly visible behind the type the whole time. The audio is one real bed with no synthetic tones. Sync: the hit at
1.00 s = frame 25, the lock onset at 10.16-10.24 s with brackets snapping at frame 256 (within 1 frame), the true
silence at 11.96-12.24 s plays under the freeze 299-306, and the drop onset at 12.28 s = frame 307 exactly.
The title card (frames 330-374) is premium and works as the cover/loop frame. The fixes below are the only things
that keep it from being "best of best". Fix them in order. Each one is a re-render of the same HyperFrames
comp plus a remux; no new assets are needed.

1. **[mograph] The name-to-title morph at frame 308 looks like a glitch (top priority).** Frame 308 double-exposes three things
   at about 50%: the roll name "VINAY KRISHAN ROHILLA" (Inter), the title "VINAY KRISHAN / ROHILLA" (Bebas), and the
   bracket corners plus the `TRK_07 SOLVED` label. That makes a 3-line overprint, and it is the cheap moment the client will notice.
   Fix: do the swap *behind* the flash. On frame 307, kill the brackets, the TRK label and the roll name (opacity 0 under the flash).
   From 308, show only the title, entering at scale 1.12 to 1.00 with blur 6 to 0 px over 4 frames (ease-out), plus the shake.
   No frame may show both typefaces at the same time.

2. **[mograph] The slam flash at frame 307 is a flat mustard full-frame wash** (mean luma 111 against 34 on either side; the logo, plate and type
   are all washed to an olive-gold card). It reads as a video glitch, not a light hit. Fix: make it a radial gold bloom centred on the
   name (y 1920), with a peak opacity of about 0.65 at the centre falling to about 0.2 at the frame edges, over 1 frame up and 3 frames decaying (307-310).
   Use a warmer colour (#F5B53C mixed toward #F05A1A rather than desaturated yellow), and keep the SF logo on top of the flash.

3. **[edit/color: plate] The opening light leak peaks 2 frames early and blanks the picture.** Frames 23-24 are an almost flat beige
   frame (luma 87 / 71 against 11 before it) with no plate detail. The music hit and the logo slam land at frame 25.
   Fix: shift the B-transition leak so its peak sits on frame 25. Cap it so the plate still shows through (peak luma about 55-60,
   with a gradient leak from one side instead of a uniform fadewhite). Re-run the LUT so it stays pale-gold, not beige.

4. **[mograph] The tracker gag is too fine to read on a phone (frames 197-255).** The 3 px pattern boxes, dashed search boxes and
   26 px `TRK_0n` labels go invisible at phone size (checked at 540 px wide). This is his craft signature and should be seen.
   Fix: line weight 3 to 6 px (the dashed box to 4 px), labels 26 to 38 px, pattern box 110x70 to 150x90. Make the red "lost"
   state flash once at full opacity before it fades. Keep everything else the same.

Accepted as-is (no change): the blue in the character line-up art (Chun-Li, Cammy, the hadouken) is the official key art and is
less than 1.5% of pixels. The roll parks early (about frame 150) and is near-static during the search. That is acceptable because the trackers
carry the motion once note 4 lands.

After the fixes: QC frames 23-26 and 305-312 at 100%, and re-check that frame 307 still lines up with the drop onset.
