import { definePreset } from '@primeuix/themes';
import Aura from '@primeuix/themes/aura';

/**
 * JobRhythm-tuned Aura preset for operational admin screens.
 * Primary is action blue #2563eb; semantic status colors stay unambiguous.
 * Badge chips use muted surface + 700 labels so 0.75rem text stays AA (fill tokens do not).
 */
export const JobRhythmPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: '#eff6ff',
      100: '#dbeafe',
      200: '#bfdbfe',
      300: '#93c5fd',
      400: '#60a5fa',
      500: '#2563eb',
      600: '#1d4ed8',
      700: '#1e40af',
      800: '#1e3a8a',
      900: '#1e3a8a',
      950: '#172554',
    },
    colorScheme: {
      light: {
        primary: {
          color: '#2563eb',
          contrastColor: '#ffffff',
          hoverColor: '#1d4ed8',
          activeColor: '#1e40af',
        },
        surface: {
          0: '#ffffff',
          50: '#f9fafb',
          100: '#f3f4f6',
        },
        formField: {
          background: '#ffffff',
          color: '#111827',
          borderColor: '#e5e7eb',
          hoverBorderColor: '#d1d5db',
          focusBorderColor: '#2563eb',
          invalidBorderColor: '#dc2626',
          borderRadius: '0',
        },
        text: {
          color: '#111827',
          hoverColor: '#111827',
          mutedColor: '#4b5563',
          hoverMutedColor: '#111827',
        },
      },
    },
  },
  components: {
    badge: {
      borderRadius: '0.5rem',
      secondary: {
        background: '{gray.100}',
        color: '{gray.600}',
      },
      success: {
        background: '{green.100}',
        color: '{green.800}',
      },
      info: {
        background: '{blue.50}',
        color: '{blue.800}',
      },
      warn: {
        background: '{amber.100}',
        color: '{amber.800}',
      },
      danger: {
        background: '{red.100}',
        color: '{red.800}',
      },
    },
    paginator: {
      root: {
        background: 'transparent',
        color: '{gray.900}',
        borderRadius: '0.5rem',
      },
      navButton: {
        borderRadius: '0.5rem',
        color: '{gray.600}',
        hoverColor: '{gray.900}',
        hoverBackground: '{gray.50}',
      },
      currentPageReport: {
        color: '{gray.600}',
      },
    },
    datatable: {
      headerCell: {
        background: '{gray.50}',
        color: '{gray.900}',
      },
      row: {
        hoverBackground: '{gray.50}',
        stripedBackground: '{gray.50}',
      },
    },
  },
});
