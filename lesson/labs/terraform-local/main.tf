terraform {
  required_version = ">= 1.4.0"
}

variable "environment" {
  type    = string
  default = "lab"
}

resource "terraform_data" "label" {
  input = "notes-${var.environment}"
}

output "resource_label" {
  value = terraform_data.label.output
}
