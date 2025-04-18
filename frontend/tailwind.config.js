/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./src/**/*.{html,js,svelte,ts}",
        "./node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}"
    ],
    safelist: ['popover-fix'],
    theme: {
        extend: {}
    },

    plugins: [require("flowbite/plugin")],
    darkMode: "class"
};
