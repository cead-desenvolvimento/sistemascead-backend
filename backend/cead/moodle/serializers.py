from collections import defaultdict
from rest_framework import serializers

from cead.models import FiDatafrequencia, FiFrequencia, FiFrequenciaMoodle


class FiDatafrequenciaSerializer(serializers.ModelSerializer):
    descricao = serializers.SerializerMethodField()

    class Meta:
        model = FiDatafrequencia
        fields = ["id", "descricao"]

    def get_descricao(self, obj):
        return str(obj)


class FiFrequenciaMoodleEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = FiFrequenciaMoodle
        fields = ["moodle_id", "ultimo_acesso", "data_consulta"]


class FiFrequenciaMoodleListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        # Carrega todas as frequências do período e pessoas envolvidas
        frequencias = FiFrequencia.objects.select_related(
            "cm_pessoa_coordenador", "ac_curso_oferta__ac_curso"
        ).filter(
            fi_datafrequencia__in=set(x.fi_datafrequencia for x in data),
            cm_pessoa__in=set(x.cm_pessoa for x in data),
        )

        # Indexar por (datafrequencia, pessoa)
        freq_index = defaultdict(list)
        for f in frequencias:
            chave = (f.fi_datafrequencia_id, f.cm_pessoa_id)
            freq_index[chave].append(f)

        # Agrupar por coordenador > curso > pessoa
        coordenadores = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        for item in data:
            chave = (item.fi_datafrequencia_id, item.cm_pessoa_id)
            freq = freq_index.get(chave, [None])[0]
            if not freq:
                continue

            coordenador_str = str(freq.cm_pessoa_coordenador)
            curso = freq.ac_curso_oferta.ac_curso
            curso_id = curso.id
            curso_nome = curso.nome
            pessoa_str = str(item.cm_pessoa)

            coordenadores[coordenador_str][curso_id, curso_nome][pessoa_str].append(
                item
            )

        # resultado retorna assim:

        # [
        # {
        #     "coordenador": "Zelune Vasconcelos de Peles Pereira 123.456.789-00",
        #     "cursos": [
        #     {
        #         "curso": "Curso de Drogas",
        #         "pessoas": [
        #         {
        #             "pessoa": "João Bolsista 123.123.123-00",
        #             "registros": [
        #             { "moodle_id": "...", "ultimo_acesso": "...", "data_consulta": "..." }
        #             ]
        #         }
        #         ]
        #     }
        #     ]
        # }
        # ]

        resultado = []
        for coordenador, cursos in coordenadores.items():
            cursos_formatados = []
            for (curso_id, curso_nome), pessoas in sorted(
                cursos.items(), key=lambda x: x[0][1]
            ):
                pessoas_formatadas = []
                for pessoa in sorted(pessoas.keys()):
                    registros_serializados = FiFrequenciaMoodleEntrySerializer(
                        pessoas[pessoa], many=True
                    ).data
                    pessoas_formatadas.append(
                        {"pessoa": pessoa, "registros": registros_serializados}
                    )

                cursos_formatados.append(
                    {"id": curso_id, "nome": curso_nome, "pessoas": pessoas_formatadas}
                )
            resultado.append({"coordenador": coordenador, "cursos": cursos_formatados})

        return resultado


class FiFrequenciaMoodleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiFrequenciaMoodle
        fields = ["cm_pessoa", "moodle_id", "ultimo_acesso", "data_consulta"]
        list_serializer_class = FiFrequenciaMoodleListSerializer
