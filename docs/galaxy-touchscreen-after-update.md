# Samsung Galaxy touchscreen not working after a One UI update: model reports

If the display works but not finger touch, start with the observation for your exact device. **This is a symptom index, not a list of supported phones.** Only the SM-G998B on HZA6 was tested with the published repair; do not flash that TAR on another model or build. A missing model means no qualifying report was included, not immunity.

## Repair verified by this project

| Model | Variant as reported | Update | Observation | Evidence |
|---|---|---|---|---|
| Galaxy S21 Ultra 5G | SM-G998B, EGY | G998BXXSJHZA6 | First probe failed with panel firmware `.26`; succeeded with `.25`. Finger touch confirmed after reboot without Magisk or the rebind script. | [Project device test](https://github.com/Majed-allababedi/vendor-ramdisk-touch-tools/releases/tag/sm-g998b-hza6-touch25-v1) |

## One UI 6.1 and closely related reports — repair not tested here

| Model | Variant as reported | Update | Observation | Evidence |
|---|---|---|---|---|
| Galaxy S21 5G | Exynos unit | One UI 6.1 | XDA author compared working recovery and failing Android driver logs and reported a root/rebind workaround; not a test of this repo’s image. | [XDA investigation](https://xdaforums.com/t/solved-with-root-one-ui-6-1-touchscreen-not-working-issue.4679358/) |
| Galaxy S21+ 5G (S21 Plus) | SM-G996B, XEF | G996BXXSBGXDH / 6.1 | Touch stopped after an unofficial replacement and then an update. | [XDA owner report](https://xdaforums.com/t/the-touchscreen-no-longer-responds-after-screen-replacement-and-updating-to-one-ui-6-1.4673853/) |
| Galaxy S21 FE 5G | SM-G990B/DS | G990BXXSBGXJ3 / 6.1 | Replacement panel stopped responding; owner reinstalled the old panel and its touch still worked. | [XDA side-by-side observation](https://xdaforums.com/t/s21-fe-5g-touch-not-working-after-one-ui-6-1-update.4702588) |
| Galaxy A54 5G | SM-A546B/DS | One UI 6.1 | Display and buttons worked but finger touch did not. Author later reported that an original replacement display restored touch. | [XDA report and follow-up](https://xdaforums.com/t/new-update-ui-6-1-touch-screen-unresponsive-on-a54-5g-sm-a546b-ds.4690126) |
| Galaxy S22 Ultra | Not specified | One UI 6.1 | Finger touch lost; S Pen still worked. | [Samsung Community](https://eu.community.samsung.com/t5/galaxy-s22-series/s22-ultra-one-ui-6-1/td-p/9935605) |
| Galaxy S23 Ultra | Not specified | One UI 6.1 | Finger touch completely unresponsive after update; S Pen worked. No controller trace supplied. | [Owner report](https://www.reddit.com/r/samsung/comments/1btoerw/s23_ultra_unresponsive_touchscreen_since_oneui_61) |
| Galaxy S23 | Title says S23; SKU not stated | One UI 6.1 | Owner reported a completely nonresponsive screen/phone. The report does not distinguish a touch-controller failure from a system freeze. | [Samsung Community](https://eu.community.samsung.com/t5/galaxy-s23-series/s23-screen-not-working-after-6-1/td-p/9632369) |
| Galaxy A52 | 4G/5G variant not stated | One UI 6.1 | Author reported loss of touch; a rollback appeared to help briefly but the problem recurred. | [Owner report and follow-up](https://www.reddit.com/r/GalaxyA52/comments/1d5i48w/touch_screen_not_working_after_one_ui_61_update/) |
| Galaxy Z Fold5 | Not specified | After update; exact build not stated | A commenter in the 6.1 discussion reported recurring episodes several times a day, not permanent first-probe failure. | [Samsung Community, May 30 reply](https://community.samsung.com/uk/conversations/other-galaxy-s-series/new-update-ui-6-1-touch-screen-unresponsive-on-s21/eu_9958836) |

## Other updates and different symptoms — not evidence for this patch

| Model | Variant as reported | Update | Observation | Evidence |
|---|---|---|---|---|
| Galaxy A53 | Refurbished unit | One UI 6 / Android 14 | Touch stopped after upgrade. Screen origin was not established. | [Samsung Community](https://lifehacker.com/tech/oneui-6-point-1-breaks-some-galaxy-displays) |
| Galaxy S20 FE 4G | SM-G780G | Software update; release not specified | Owner reported loss of touch after updating; this is not a One UI 6.1 report. | [XDA](https://xdaforums.com/t/touch-screen-not-working-after-update-to-the-last-firmware-in-s20-fe-4g-solved.4659865) |
| Galaxy A14 | Variant not established by original post | One UI 7 | Owner reported the screen became unresponsive a day later; cause not established. | [iFixit](https://www.ifixit.com/Answers/View/913656/Why+is+my+screen+becoming+unresponsive+after+One+UI+7+update) |
| Galaxy M34 | Not specified | Update version not stated | Owner reported no touch after installing an update; no build or diagnostic log supplied. | [Samsung Members](https://r2.community.samsung.com/t5/Galaxy-M/My-samsung-galaxy-m34-update-install-and-screen-not-touch/td-p/22350036) |
| Galaxy Z Fold4 | Inner display | One UI 6.1.1 | Inner screen lit up and rotated but no longer registered touch the day after updating. | [Samsung Community](https://us.community.samsung.com/t5/Galaxy-Z-Series/Fold4-inside-touch-screen-not-working-after-6-1-1-update/td-p/3027900) |
| Galaxy Z Flip5 | Not specified | One UI 6.1.1 | Incorrect touch coordinates and ghost taps only while charging; normal when unplugged. | [Owner report](https://www.reddit.com/r/galaxyzflip/comments/1gj1nzj/touchscreen_issue_after_updating_to_one_ui_611/) |
| Galaxy Z Flip6 | Not specified | Reported as 6.1.1 | A commenter reported delayed input after unfolding, restored by locking/unlocking. | [Owner comment](https://www.reddit.com/r/galaxyzflip/comments/1gj1nzj/touchscreen_issue_after_updating_to_one_ui_611/) |

**Two important lookalikes:** Samsung documented a [Galaxy Z Fold4 / Fold5 One UI 8 center-screen touch issue](https://www.samsung.com/us/support/troubleshoot/TSG10007643) tied to maximum Screen Zoom and a multi-window setting. For the S23 series, [SamMobile reported Samsung’s Google Discover explanation](https://www.sammobile.com/news/samsung-offers-temporary-fix-galaxy-s23-touchscreen-issue-one-ui-6-1) for touches that register only after repeated taps. Neither explanation establishes a failed early-boot panel update. A series-wide advisory is not a confirmed case on every SKU.

## How entries were selected

We searched model names and variants across Galaxy S, FE, A, M, Z and Tab families, prioritizing One UI 6.1 and replacement-panel reports. Rows require a named model, an update followed by a touch or closely related responsiveness symptom, and a traceable source. Community posts hosted by Samsung are owner reports, not Samsung diagnoses. We did not add every phone on an update rollout list, infer regional model codes, or count green lines, S Pen-only failures or a black display alone as lost finger touch. This is not an exhaustive manufacturer inventory.

To add or correct a row, [open an issue](https://github.com/Majed-allababedi/vendor-ramdisk-touch-tools/issues) with the exact model/build, a public source, whether finger touch or only the pen failed, and what happened on reboot. A compatibility claim additionally requires early-probe evidence and a physical test; omit serial numbers and personal logs.
