from rest_framework.renderers import BaseRenderer


class CSVRenderer(BaseRenderer):
    media_type = "text/csv"
    format = "csv"
    charset = "utf-8"

    def render(self, data, media_type=None, renderer_context=None):
        if isinstance(data, dict) and "detail" in data:
            return f'Erro: {data["detail"]}'.encode("utf-8")

        import csv
        from io import StringIO

        output = StringIO()

        # Adicionando o BOM no início
        output.write("\ufeff")

        writer = csv.writer(
            output, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )

        if data and isinstance(data, list):
            writer.writerow(data[0].keys())
            for row in data:
                writer.writerow(row.values())

        return output.getvalue().encode("utf-8")
