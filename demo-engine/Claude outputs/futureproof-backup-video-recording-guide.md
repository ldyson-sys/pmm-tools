# Futureproof backup video: recording guide

Owner: Lewis. Deadline: file in the organizer's hands before Tuesday 15 September, 11:45. Purpose: the video the emcee plays if connectivity dies during Gabe's live MCP moment. It must show exactly what the audience would have seen live, nothing more.

Confirmed setup (11 September): live demo runs on Gabe's laptop, the laptop screen is projected, prompts are pasted from a prompt card. No voice input, no phone. The recording therefore mirrors that: a screen capture of the Claude desktop app with pasted prompts, no narration, plus the Maximizer proof screens.

## 0. Before you record: three gates (Friday)

**Gate 1: the data.** Run the four questions against the tenant and compare to the QA test (`futureproof-qa-test-four-questions.md`). As of Friday morning the coverage-decay half of Q1a fails (Cameron has no contact logged; Hartfield and Vincent sit under 90 days). Run the coverage-decay script from `futureproof-qa-fixes-q2-q3.md` first. Do not record until Q1a returns exactly Cameron, Hartfield and Vincent.

**Gate 2: the wording.** Freeze the prompt card only after three clean runs per question. The recorded wording and the live wording must be identical; if Gabe pastes something different on stage from what the backup shows, the backup is useless.

**Gate 3: the definitions.** Set up a Claude Project and put the definitions in its custom instructions (quiet = 60 or more days since last contact, most valuable = Segmentation A Client, idle cash = household cash above $100,000). Record inside that project. Gabe demos from the same project.

## 1. Prepare the laptop

Do all of this on the laptop that will be used, ideally Gabe's, so the recording matches the room.

- Turn on Do Not Disturb. Quit Slack, Teams, Outlook, Mail. Close every window except Claude and a Maximizer browser tab.
- Claude desktop app: press Cmd and plus two or three times so the text is readable from the back of a room. Aim for roughly 12 to 15 chat lines visible at once. Note the zoom level and use the same one live.
- Light theme. The room is unknown; light projects more reliably.
- Start a fresh chat inside the Project for every take. Name it something neutral ("Adam's book"). No earlier answers may be visible.
- Prompt card open on your phone or printed. Never in a window on the recording screen.
- Maximizer: log in beforehand, open the Cameron household in a browser tab so the switch after Q1b is one click. Check the tab shows no other client names in a sidebar or recent list.
- Collapse the tool-call chips after each answer so the screen shows the answer, not the plumbing. Practise the click once before recording.

## 2. Recording tool and dimensions

Use the built-in macOS screenshot toolbar. Nothing to install, nothing to configure.

1. Press Shift-Cmd-5.
2. Choose Record Selected Portion.
3. Drag a box. The dimensions show while you drag: make it exactly 1920 by 1080. That is 16:9, which fills a projector edge to edge. A full MacBook screen is 16:10 and would letterbox.
4. Position the Claude window inside the box so the chat fills it. Later, the Maximizer tab goes in the same box.
5. Click Options: Save to Desktop, Show Mouse Clicks ON, Microphone NONE. There is no narration; the emcee talks over the video live, the same as he would over the real thing.
6. Click Record. Press Shift-Cmd-5 again or the stop button in the menu bar to finish.

On a Retina display the file will be captured at 3840 by 2160 pixels. That is fine; it exports down to 1080p cleanly.

## 3. Record

One take per question is not enough: record one continuous master three times, then cut it into per-question clips.

Master take structure:
1. Start recording. Two seconds of a clean, empty chat before you touch anything.
2. Paste Q1a. Hit Enter. Do not move the mouse during the wait. The wait is part of what the audience would see; do not cut it out later unless it runs past 30 seconds.
3. When the answer lands, leave it on screen for 8 seconds. Collapse the tool chips.
4. Paste Q1b. When the confirmation lands, switch to the Maximizer tab, open the Cameron household, show the task with its reason. Hold 6 seconds. Switch back.
5. Paste Q1c. Hold the answer 10 seconds.
6. Paste Q2, Q3, Q4 in order. Hold each answer 6 seconds.
7. Two seconds of still screen. Stop.

Between takes: delete the three tasks Q1b created (or the next take shows six), and re-run the coverage-decay script, because task creation likely resets Date Last Contacted to today and the next Q1a will return nobody. Confirm Q1a before starting the next take.

Reject any take where Claude names a household that should not be there, invents a fact, or quotes a figure that does not match the tenant. The backup must be a run you would be proud of live, not just a run that finished.

## 4. Package

- Pick the cleanest master. Open it in QuickTime Player. Edit, Trim to cut the dead time before the first paste and after the last answer. Save.
- Cut per-question clips from the same master: QuickTime, Edit, Trim again on a duplicate, one clip per question. The emcee needs to jump straight to whichever question Gabe was on when the connection dropped.
- Export every file: File, Export As, 1080p. That gives MP4, H.264, 1920 by 1080, 30 fps. Each file should be well under 500 MB.
- Filenames: `Maximizer-MCP-backup-MASTER.mp4`, `Maximizer-MCP-backup-Q1.mp4`, `Maximizer-MCP-backup-Q2.mp4`, `Maximizer-MCP-backup-Q3.mp4`, `Maximizer-MCP-backup-Q4.mp4`. Sizzle: `Maximizer-sizzle-3min.mp4`.
- Add `README.txt` with the run order and the timestamp of each question in the master.
- Do not add music, captions, transitions or a title card. The live demo has none of those, and the video is meant to be indistinguishable from it.

## 5. Deliver and test

- Send the organizer a download link by Sunday night so he can confirm it plays on his machine. Ask him which player he uses; QuickTime, VLC and PowerPoint all handle the spec above.
- Put every file on a USB stick and on the desktop of Gabe's laptop. Bring both.
- Play the master start to finish on the laptop before you leave for the venue. Check: text readable from two metres, no notification banners, nothing on screen that no longer matches the live tenant (household names, figures, the Cameron task).
- On the day, tell the emcee which clip maps to which question before the session starts, so he is not scrubbing a timeline on stage.

## 6. Time budget

Friday: run the coverage-decay fix, pass Gate 1, freeze wording, set up the Project. Saturday: record and package. Sunday: send link, load USB and laptop. Monday: final Gabe run-through at the recording zoom level, play the backup once so he knows what the emcee will show. Anything that slips past Sunday night puts the file at risk.
