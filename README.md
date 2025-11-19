# 🟨 Sticky Notes Add-on for Anki Desktop

**A powerful Markdown-enabled sticky notes add-on for Anki with an intuitive live preview editor.**

![Preview](https://i.imgur.com/0example.png)

## Features

### Rich Markdown Support

Write notes with full Markdown formatting:

- **Bold**, _Italic_, ~~Strikethrough~~, `Inline Code`

- Headings (H1, H2, H3)

- Bullet lists

- Links `[text](https://)`

- Horizontal rules `---`

### Smart Visual Editor with Markdown toolbar

![Preview](https://i.imgur.com/0example.png)

The editor provides live preview of sticky notes while you make it:

- Select text and click to instantly wrap it with formatting.
- Toggle formatting on/off with a second click on toolbar button.

### Live Preview

See exactly how your note will appear on the card as you type.
![Preview](https://i.imgur.com/0example.png)

### Customization Options

- 6 color themes: yellow, green, blue, pink, purple, orange.

- Adjustable font size and family.

- Configurable width and height of sticky note.

### Sticky Notes Storage

Your sticky notes data is stored within collection.media folder of your Anki profile, which get synced along with your media files.

However, this approach has a drawback which is not being able to search sticky notes in Card Browser.

I had to chose this because to make sticky notes searchable in card browser, I would have to add another extra 'StickyNotes' field to the note type. This could've break the updates for shared deck on AnkiHub, since deck updates are controlled through fields in shared deck from AnkiHub.

If anyone who can find a way to solve this problem, please add a PR or give your suggestions.

Now, since sticky notes data is stored in a single \_sticky.JSON file in media folder, it can be synced.

Sticky Notes are stored in this format in JSON.
Here are 2 sticky notes attached to one card with ID `1763368231436`.

```json
{
  "1763368231436": [
    {
      "data": "**Hello World**\n",
      "color": "yellow",
      "font_size": 18,
      "font_family": "Comic Sans MS",
      "width": 300,
      "height": 150
    },
    {
      "data": "### Hello\n_This is a note_",
      "color": "pink",
      "font_size": 19,
      "font_family": "Verdana",
      "width": 200,
      "height": 100
    }
  ]
}
```

### Import & Export Sticky Notes

Sticky Notes can be imported and exported as JSON files with respected to decks. You can specifically import or export all the sticky notes of a particular deck.

### Automatic Grid Layout

Notes arrange themselves cleanly using Grid layout—no overlaps, no manual positioning required.
To achieve this I used [PackeryJS](https://packery.metafizzy.co/), that can automatically spread sticky notes into _Bento_ layout.

## Installation

1. Download the `.ankiaddon` file from the releases page

2. In Anki, go to Tools → Add-ons → Install from file...

3. Select the downloaded file

4. Restart Anki

5. Press `Ctrl+Shift+S` on any card to create your first note

## How to use

To use this add-on simply Install it from AnkiWeb or use the above guide to install it from Github releases.

Follow these instructions:

- After installing the add-on, restart your Anki Desktop.
- Visit the card where you want to add the sticky notes, Open the review or answer screen (back side of the card).
- Press `CTRL+SHIFT+S` to add sticky notes (You can also find the `add sticky note` button in the `more` option in the _bottom right corner_ of review screen)
- This will open the sticky notes live preview markdown editor.
- Create your beautiful sticky note, and press `save` to add it to the review screen of the card.
- Later, on hovering to the card, you can see use two functions to `edit` and `delete` the card.

## Workflow Tools

- **Keyboard shortcut**: `Ctrl+Shift+S` on review answer screen to add sticky notes or to open sticky notes editor.

- **Export/Import**: Back up and share your notes

- **Compatible**: Works with Anki 2.1.66+ including the latest Qt6 versions (25.09+)

## Usage

### Basic Operations

- **Add/Edit Note**: Press `Ctrl+Shift+S` or right-click → Sticky Notes → Add/Edit

- **Toggle Visibility**: Click the sticky note icon in the reviewer toolbar

- **Delete Note**: Open the editor and click Delete

- **Resize/Move**: Drag the corners or edges of any note

### Editor Shortcuts (Coming soon)

- `Ctrl+B` — Bold

- `Ctrl+I` — Italic

- `Ctrl+Shift+S` — Strikethrough

- `Ctrl+1/2/3` — Heading 1/2/3

- `Ctrl+L` — Insert Link

## Use Cases

This add-on works well for:

- **Medical students** adding quick explanations or mnemonics to complex diagrams

- **Language learners** writing example sentences or grammar notes

- **General study** organizing supplementary information without editing the original card

The Markdown support means you can maintain clean, readable formatting without cluttering your card templates.

## Technical Details

- Built with PyQt6 and Packery.js

- Lightweight custom Markdown parser

- Tested on Windows, macOS, and Linux

- Compatible with Anki 2.1.66+ (including Qt6 versions)

## Screenshots

_(Additional screenshots showing various features will be added here)_

## Support

If you encounter issues or have suggestions:

- Check the issues page on GitHub

- Report bugs with your Anki version and system details

## License

This add-on is free and open source.

## Donate to the developer

If you think this add-on is worth paying for, buy the developer some tea or coffee.

Here are the payment information

---

**Contributions and feedback are welcome.**
