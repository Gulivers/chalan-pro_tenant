import { definePreset } from '@primeuix/themes';
import Aura from '@primeuix/themes/aura';

/**
 * JobRhythm-tuned Aura preset for operational admin screens.
 * Primary is action blue #2563eb; semantic status colors stay unambiguous.
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
          borderRadius: '0.5rem',
        },
      },
    },
  },
});
