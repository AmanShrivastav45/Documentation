import typography from '@tailwindcss/typography'

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        'text-primary': '#393946',
        'text-secondary': '#454554',
        'text-strong': '#17171c',
        'text-muted': '#67677e',
        'link-blue': '#1866d4',
        'surface-white': '#ffffff',
        'surface-light-gray': '#f4f4f6',
        'border-subtle': '#aeaebc',
        'border-light': '#d8d8df',
        'badge-warning-bg': '#fef0e6',
        'badge-warning-text': '#9f2000',
      },
      fontFamily: {
        display: ['Poppins', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
      borderRadius: {
        sm: '4px',
        md: '6px',
        lg: '8px',
        xl: '10px',
      },
      typography: {
        DEFAULT: {
          css: {
            '--tw-prose-headings': '#17171c',
            '--tw-prose-body': '#393946',
            '--tw-prose-links': '#1866d4',
            fontFamily: 'Inter, sans-serif',
            h1: { fontFamily: 'Poppins, sans-serif' },
            h2: { fontFamily: 'Poppins, sans-serif' },
          },
        },
      },
    },
  },
  plugins: [typography],
}
