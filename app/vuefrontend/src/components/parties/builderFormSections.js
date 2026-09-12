export const BUILDER_FORM_SECTIONS = [
  {
    title: "Identity",
    grid: "identity",
    fields: ["name", "rfc", "types", "category", "is_active"],
  },
  {
    title: "Pricing",
    grid: "pricing",
    fields: [
      "trim_amount",
      "rough_amount",
      "travel_price_amount",
      "default_price_type",
    ],
  },
  {
    title: "Address",
    grid: "address",
    fields: [
      "street",
      "floor_office",
      "city",
      "state",
      "zipcode",
      "country",
    ],
  },
  {
    title: "Contact",
    grid: "contact",
    fields: ["phone", "email"],
  },
  {
    title: "Roles",
    grid: "flags",
    fields: ["customer_rank", "supplier_rank"],
  },
];
