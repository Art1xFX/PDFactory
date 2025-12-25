from import_export import resources

from course.models import Certificate


class CertificateResource(resources.ModelResource):
    class Meta:
        model = Certificate
        import_id_fields = ("first_name", "last_name", "intake")
        fields = ("first_name", "last_name", "intake")

    def before_import(self, dataset, **kwargs):
        if "intake" not in dataset.headers:
            dataset.headers.append("intake")
        super().before_import(dataset, **kwargs)

    def before_import_row(self, row, **kwargs):
        if not row.get("intake"):
            row["intake"] = kwargs["intake"].pk
        return super().before_import_row(row, **kwargs)

    def before_save_instance(self, instance: Certificate, row, **kwargs):
        # Pass `dry_run` flag to the model instance to avoid saving files during dry runs.
        instance.dry_run = kwargs.get("dry_run", False)
        super().before_save_instance(instance, row, **kwargs)

    def get_user_visible_fields(self):
        return [
            self.fields["first_name"],
            self.fields["last_name"],
        ]
