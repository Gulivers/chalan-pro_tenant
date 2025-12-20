import axios from "axios";

export default {
  data() {
    return {
      optionsMap: {},
    };
  },
  methods: {
    async loadOptionsForSchema(schema) {
      for (const [key, config] of Object.entries(schema)) {
        if (config.type === "select" && config.optionsEndpoint) {
          try {
            const res = await axios.get(config.optionsEndpoint);
            const rawOptions = res.data;

            this.optionsMap[key] = rawOptions.map((opt) => ({
              value: opt.id || opt.value,
              label: opt.name || opt.label,
            }));
            console.log(
              // `📥 Options loaded for "${key}":`,
              this.optionsMap[key]
            );
          } catch (err) {
            console.error(`❌ Error loading options for ${key}:`, err);
            this.optionsMap[key] = [];
          }
        }
        //Si el campo tiene options directamente en el schema (como conversion_sign)
        else if (config.options && Array.isArray(config.options)) {
          this.optionsMap[key] = config.options;
        }
      }
    },
  },
};
