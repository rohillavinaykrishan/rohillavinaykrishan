# sh010 roto v001 - person holdout (director note 20, 2x)

matte/matte.%04d.png: 52 frames (s0-s51 = trailer src 2982-3033), 2560x1072 (exactly 2x plate 1280x536), 8-bit gray,
white = holdout (person in front of CG), straight (not premultiplied). Use: CG * (1 - matte), after scaling to comp res.
Includes all fighters. Does NOT deliberately include the rotor blade/helicopter (small fragments on s0, s35-36, s48-50 come
along with the left man; all far from the monument).

Pipeline
1. plate/ extracted from source/trailer.mp4 (select 2982-3033, crop 1280:536:0:92); pixel-identical to color/v001/plate_src.
2. rembg u2net_human_seg --mode matte (raw/rembg_human_matte.mov -> raw/human/). It DROPS whole fighters on s8-10, s13-14,
   s17-30, s28-41, s43-50, so on its own it is not usable.
3. SAM 2 tiny, multi-object, keyframe prompts (scripts/sam_multi.py, scripts/people_prompts.json; forward pass):
   woman, bigman, whiteman; plus womanhead on s38-51 (scripts/head_prompts_s38.json) for her motion-blurred hair.
4. scripts/refine2x.py: max(rembg, SAM) -> cubic 2x -> cv2.ximgproc.guidedFilter(guide=plate 2x, r=4, eps=1e-3)
   -> temporal median 3 -> erode 1 px -> gaussian feather sigma 2 px.
5. scripts/check_sheet.py -> review/matte_check_v001.png; scripts/bbox_sheet.py -> review/monument_bbox_vs_blade_heli.png.

Blade / helicopter vs monument (layout/v001/anchor.json, anchor x 2.0 y 20.75): blade stays y <= ~80 px (plate) on all frames,
monument bbox top >= 143; heli body x <= ~260 (s28-45) / <= ~500 (s46-51) vs bbox x0 >= 552 / >= 708. No overlap at any
frame, so no blade matte (SAM blade run was stopped). Holdout coverage inside the monument bbox is continuous (23-53%), no drops.
Known: s51 far-left man only partly matted (outside the bbox).
