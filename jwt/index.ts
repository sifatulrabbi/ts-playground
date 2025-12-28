import jwt from "jsonwebtoken";

const token = jwt.sign(
  {
    org_id: "4f7257ba-edcf-4dfc-a7fd-48fc719f1eb2",
    external_user_id: "ef61e24a-3e2f-47c9-9e38-b71d8a9f992b",
    sub: "4f7257ba-edcf-4dfc-a7fd-48fc719f1eb2",
  },
  "secret-key",
);
console.log(token);
