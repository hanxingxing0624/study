document.addEventListener("alpine:init", () => {
    Alpine.data("tagInput", () => ({
        tagText: "",
        tags: [],
        addTag() {
            const name = this.tagText.trim();
            if (name && !this.tags.includes(name)) {
                this.tags.push(name);
            }
            this.tagText = "";
        },
        removeTag(name) {
            this.tags = this.tags.filter(t => t !== name);
        },
    }));
});

// KaTeX auto-render on htmx content swaps
document.addEventListener("htmx:afterSwap", () => {
    if (typeof renderMathInElement !== "undefined") {
        renderMathInElement(document.body, {
            delimiters: [
                { left: "$$", right: "$$", display: true },
                { left: "$", right: "$", display: false },
            ],
        });
    }
});
