export const BUILDER_FORM_SECTIONS = [
  {
    titleKey: "parties.sectionRoles",
    grid: "flags",
    fields: ["customer_rank", "supplier_rank", "is_active"],
  },
  {
    titleKey: "parties.sectionIdentity",
    grid: "identity",
    fields: ["name", "rfc", "types", "category"],
  },
  {
    titleKey: "parties.sectionPricing",
    grid: "pricing",
    fields: [
      "trim_amount",
      "rough_amount",
      "travel_price_amount",
      "default_price_type",
    ],
  },
  {
    titleKey: "parties.sectionAddress",
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
    titleKey: "parties.sectionContact",
    grid: "contact",
    fields: ["phone", "email"],
  },
];
