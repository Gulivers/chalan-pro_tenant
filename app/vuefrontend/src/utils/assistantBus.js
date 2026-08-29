import mitt from 'mitt';

/** Lightweight event bus for JobRhythm Assistant panel open/close. */
export const assistantBus = mitt();

export const ASSISTANT_OPEN = 'assistant:open';
export const ASSISTANT_CLOSE = 'assistant:close';
export const ASSISTANT_TOGGLE = 'assistant:toggle';

export function openAssistant(payload = {}) {
  assistantBus.emit(ASSISTANT_OPEN, payload);
}

export function closeAssistant() {
  assistantBus.emit(ASSISTANT_CLOSE);
}

export function toggleAssistant() {
  assistantBus.emit(ASSISTANT_TOGGLE);
}
