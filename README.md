# 🟨 Sticky Notes Add-on for Anki Desktop

**A powerful, Markdown-enabled sticky notes add-on for Anki with an intuitive live preview editor.**

![Preview](https://i.imgur.com/UCyItw0.jpeg)

## Installation

Install via [AnkiWeb]() or [GitHub Releases](https://github.com/Ankitupa007/anki-stickynotes/releases).

1. Download the `.ankiaddon` file from the Releases page or install via AnkiWeb.
2. In Anki, go to **Tools → Add-ons → Install from file...**
3. Select the downloaded file.
4. Restart Anki.
5. Press **`Ctrl+Shift+S`** on any card review/answer screen to create your first note.

## How to Use

To use this add-on, simply install it from AnkiWeb or GitHub Releases and follow the steps below:

- After installing the add-on, restart Anki Desktop.
- Visit the card where you want to add sticky notes, and open the **review or answer screen** (back side of the card).
- Press **`Ctrl+Shift+S`** to add a sticky note (you can also find the **Add Sticky Note** button under the **More** menu in the bottom-right corner).
- This will open the sticky notes live preview Markdown editor.
- Create your sticky note and press **Save** to add it to the review screen.
- Later, hover over the card to see the **Edit** and **Delete** options for the sticky note.

## Features

### Rich Markdown Support

Write notes using full Markdown formatting:

- **Bold**, _Italic_, ~~Strikethrough~~, `Inline Code`
- Headings (H1, H2, H3)
- Bullet lists
- Links `[text](https://...)`
- Horizontal rules (`---`)

### Smart Visual Editor with Markdown Toolbar

![Preview](https://i.imgur.com/Bm5p7tK.jpeg)

The editor provides a live preview of your sticky notes as you write:

- Select text and click a toolbar button to instantly wrap it in formatting.
- Toggle formatting on/off with a second click.

### Live Preview

See exactly how your note will appear on the card as you type.

### Customization Options

- Six color themes: yellow, green, blue, pink, purple, orange
- Adjustable font size and family
- Configurable sticky note width and height

### Sticky Notes Storage & Syncing (IMPORTANT)

Your sticky notes data is stored inside your Anki profile's **collection.media** folder. These files sync along with your media.

However, this approach has one drawback:
**Sticky notes cannot be searched in the Card Browser.**

I chose this method because making sticky notes searchable would require adding an extra `StickyNotes` field to every note type, which would break updates for shared decks on AnkiHub—deck updates are controlled through fields.

If someone finds a solution, please submit a PR or share suggestions.

Since all sticky notes are stored in a single `_sticky.json` file inside the media folder, the notes sync correctly.

Here is an example of sticky notes stored for a card with ID `1763368231436`:

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

Sticky notes can be imported or exported as JSON files, specific to decks. You can import/export all sticky notes belonging to a particular deck.

### Automatic Grid Layout

Notes are automatically arranged using a clean grid layout—no overlaps, no manual dragging required.

This is powered by **PackeryJS**, which creates a Bento-style layout automatically.

## Workflow

- **Keyboard shortcut:** `Ctrl+Shift+S` on the review/answer screen to add or open sticky notes.
- **Export/Import:** Back up and share your notes.
- **Compatibility:** Works with Anki 2.1.66+ including the latest Qt6 versions (25.09+).

### Basic Operations

- **Add Note:** `Ctrl+Shift+S` or right-click → Sticky Notes → Add
- **Delete Note:** Hover over the card for the Delete button, or open the editor and click **Delete**

## Use Cases

This add-on is great for:

- **Students** adding quick explanations or mnemonics to complex diagrams
- **Language learners** adding example sentences or grammar notes
- **General study** adding supplementary information without modifying the original card

Markdown support ensures clean and readable formatting without cluttering card templates.

## Technical Details

- Built with PyQt6 and Packery.js
- Lightweight custom Markdown parser
- Tested on Windows and macOS
- Compatible with Anki 2.1.66+ (including Qt6 versions)

## License

This add-on is free and open source.

## Support the Development

I am a solo developer dedicating my time to create and maintain this add-on for the Anki community.

If you find this add-on helpful, please consider supporting its development.

**Indian patrons:**
UPI ID: `ankit.upa007@oksbi`

**International patrons:**
PayPal: [paypal.me/thisisankitupadhyay](https://paypal.me/thisisankitupadhyay)

---

**Contributions and feedback are welcome.**
Report bugs, request features, or submit a PR.
For contact, email: **[theankitnet@gmail.com](mailto:theankitnet@gmail.com)**

---
