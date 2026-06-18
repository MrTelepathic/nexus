import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Telegram theme CSS variables (set dynamically by ThemeProvider)
        tg: {
          bg: 'var(--tg-theme-bg-color, #ffffff)',
          'bg-secondary': 'var(--tg-theme-secondary-bg-color, #f0f0f0)',
          text: 'var(--tg-theme-text-color, #000000)',
          'text-secondary': 'var(--tg-theme-hint-color, #999999)',
          link: 'var(--tg-theme-link-color, #2481cc)',
          button: 'var(--tg-theme-button-color, #2481cc)',
          'button-text': 'var(--tg-theme-button-text-color, #ffffff)',
          'button-secondary': 'var(--tg-theme-secondary-button-color, #efeff3)',
          'button-secondary-text': 'var(--tg-theme-secondary-button-text-color, #2481cc)',
          accent: 'var(--tg-theme-accent-text-color, #2481cc)',
          destructive: 'var(--tg-theme-destructive-text-color, #e53935)',
          'section-bg': 'var(--tg-theme-section-bg-color, #ffffff)',
          'section-header': 'var(--tg-theme-section-header-text-color, #6d7f8f)',
          'section-separator': 'var(--tg-theme-section-separator-color, #e0e0e0)',
          'subtitle-text': 'var(--tg-theme-subtitle-text-color, #6d7f8f)',
        },
      },
      fontFamily: {
        system: [
          'var(--tg-theme-font, -apple-system)',
          'system-ui',
          'sans-serif',
        ],
      },
    },
  },
  plugins: [],
}

export default config
