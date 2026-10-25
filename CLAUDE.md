# MzPreloved

## Videos: always make two versions

Whenever I ask for a video, make **two versions** of it so I can compare and pick:

1. **Hypit version**: built with the `hypit` skill and the Hypit CLI.
2. **HyperFrames version**: built with the `hyperframes` skills.

Both versions use the same script and the same voiceover, so the only difference is how each tool designs and edits the video.

- Write the script first, following the `content-principles` skill.
- Make the narration once with ElevenLabs (`text-to-speech` skill) and use that audio file in both versions.
- When both are rendered, show them side by side and briefly say how they differ.

## Setup notes

- The Hypit CLI is installed with `npm i -g @hypit/hypit`. The cloud machine resets between sessions, so reinstall it if `hypit` is missing.
- ElevenLabs reads its key from the `ELEVENLABS_API_KEY` environment variable. Never ask for the key in chat.
