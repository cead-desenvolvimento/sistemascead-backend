from collections import Counter
from datetime import datetime, timedelta, time

from django.core.mail import EmailMessage
from django.utils import timezone

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cead.messages import (
    EMAIL_ASSINATURA,
    EMAIL_DUVIDAS_PARA_O_SUPORTE,
    EMAIL_ENDERECO_NAO_MONITORADO,
    ERRO_SESSAO_INVALIDA,
)
from cead.models import (
    CmPessoa,
    TrDisponibilidadeEquipe,
    TrEspacoFisico,
    TrIndisponibilidadeEquipe,
    TrLimites,
    TrTermo,
    TrTransmissao,
    TrTransmissaoEmail,
    TrTransmissaoHorario,
    TrTransmissaoRecusada,
)
from cead.settings import EMAIL_HOST_USER
from cead.utils import gerar_hash

from .api_docs import *
from .messages import *
from .permissions import *
from .serializers import *
from .utils import *


class TermoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsRequisitanteTransmissao]

    @extend_schema(**TERMO_VIEW_DOCS["get"])
    def get(self, request):
        try:
            limites = TrLimites.objects.get(id=1)  # Singleton
        except TrLimites.DoesNotExist:
            return Response(
                {"detail": ERRO_GET_LIMITES},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            pessoa = CmPessoa.objects.get(cpf=request.user.username)
        except CmPessoa.DoesNotExist:
            return Response(
                {"detail": ERRO_GET_REQUISITANTE},
                status=status.HTTP_404_NOT_FOUND,
            )

        termo = TrTermo.objects.order_by("-id").first()
        if not termo:
            return Response(
                {"detail": ERRO_GET_TERMO_SEM_TERMO},
                status=status.HTTP_404_NOT_FOUND,
            )

        hoje = timezone.now().date()

        recusadas_ids = TrTransmissaoRecusada.objects.values_list(
            "tr_transmissao_id", flat=True
        )

        # Pedidos ativos: não recusados e com algum horário futuro
        pedidos_ativos = (
            TrTransmissao.objects.filter(cm_pessoa=pessoa)
            .exclude(id__in=recusadas_ids)
            .filter(trtransmissaohorario__inicio__date__gte=hoje)
            .distinct()
            .count()
        )

        if pedidos_ativos >= limites.limite_por_pessoa:
            return Response(
                {"detail": ERRO_LIMITES_LIMITE_POR_PESSOA},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(TermoSerializer(termo).data)

    # Cria um hash para controle de fluxo nos proximos passos
    # Se a pessoa nao clicar que aceitou, nao passara do initial das proximas classes
    @extend_schema(**TERMO_VIEW_DOCS["post"])
    def post(self, request):
        request.session.flush()

        agora = timezone.now()

        request.session["aceite_termo"] = {
            "agora": agora.isoformat(),
            "hash": gerar_hash(str(agora)),
        }

        return Response({"detail": OK_ACEITE_TERMO}, status=status.HTTP_200_OK)


class EspacoFisicoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsRequisitanteTransmissao]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        aceite = request.session.get("aceite_termo")
        if not aceite:
            raise ValidationError({"detail": ERRO_ACEITE_TERMO_NAO_REALIZADO})

        momento_str = aceite.get("agora")
        hash_armazenado = aceite.get("hash")

        if not momento_str or not hash_armazenado:
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            momento = timezone.datetime.fromisoformat(momento_str)
            if timezone.is_naive(momento):
                momento = timezone.make_aware(momento, timezone.get_current_timezone())
        except Exception:
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        if hash_armazenado != gerar_hash(str(momento)):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        if timezone.now() - momento > timedelta(hours=1):
            raise ValidationError({"detail": ERRO_ACEITE_TERMO_EXPIRADO})

    @extend_schema(**ESPACO_FISICO_VIEW_DOCS["get"])
    def get(self, request):
        espacos_fisicos = TrEspacoFisico.objects.filter(ativo=True)

        if not espacos_fisicos:
            return Response(
                {"detail": ERRO_GET_ESPACO_FISICO_SEM_ESPACO_FISICO},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            EspacoFisicoSelecionarSerializer(espacos_fisicos, many=True).data
        )

    @extend_schema(**ESPACO_FISICO_VIEW_DOCS["post"])
    def post(self, request):
        espaco_id = request.data.get("id")

        if not espaco_id:
            raise ValidationError({"detail": ERRO_POST_ESPACO_ID_OBRIGATORIO})

        try:
            espaco = TrEspacoFisico.objects.get(id=espaco_id, ativo=True)
        except TrEspacoFisico.DoesNotExist:
            raise ValidationError({"detail": ERRO_ESPACO_NAO_ENCONTRADO})

        request.session["espaco_fisico"] = espaco.id
        request.session["espaco_fisico_hash"] = gerar_hash(espaco.id)

        return Response(
            {"detail": OK_ESPACO_SELECIONADO},
            status=status.HTTP_200_OK,
        )


class DatasDisponiveisAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsRequisitanteTransmissao]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        aceite = request.session.get("aceite_termo")
        if not aceite:
            raise ValidationError({"detail": ERRO_ACEITE_TERMO_NAO_REALIZADO})

        momento_str = aceite.get("agora")
        hash_armazenado = aceite.get("hash")

        if not momento_str or not hash_armazenado:
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            momento = timezone.datetime.fromisoformat(momento_str)
            if timezone.is_naive(momento):
                momento = timezone.make_aware(momento, timezone.get_current_timezone())
        except Exception:
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        if hash_armazenado != gerar_hash(str(momento)):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        if timezone.now() - momento > timedelta(hours=1):
            raise ValidationError({"detail": ERRO_ACEITE_TERMO_EXPIRADO})

        if "espaco_fisico" not in request.session:
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if "espaco_fisico_hash" not in request.session:
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["espaco_fisico_hash"] != gerar_hash(
            request.session["espaco_fisico"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            TrEspacoFisico.objects.get(id=request.session["espaco_fisico"])
        except TrEspacoFisico.DoesNotExist:
            raise ValidationError({"detail": ERRO_ESPACO_NAO_ENCONTRADO})

        request.espaco_fisico = request.session["espaco_fisico"]

    @extend_schema(**DATAS_DISPONIVEIS_VIEW_DOCS["get"])
    def get(self, request):
        # Dias permitidos da semana (ex: ['1', '3', '5'] para seg/qua/sex)
        dias_permitidos = set(
            TrDisponibilidadeEquipe.objects.values_list("dia_semana", flat=True)
        )

        if not dias_permitidos:
            return Response(
                {"detail": ERRO_DATA_EQUIPE_INDISPONIVEL},
                status=status.HTTP_404_NOT_FOUND,
            )

        espaco = TrEspacoFisico.objects.get(id=request.espaco_fisico)
        limites = TrLimites.objects.get(pk=1)

        hoje = timezone.localdate()
        data_inicial = hoje + timedelta(days=limites.dias_de_antecedencia)
        limite_agenda = hoje + timedelta(days=limites.dias_de_agenda_aberta)

        # IDs de transmissões recusadas
        recusadas_ids = TrTransmissaoRecusada.objects.values_list(
            "tr_transmissao_id", flat=True
        )

        # Busca todas as transmissões do espaço físico
        transmissoes_ids = (
            TrTransmissao.objects.filter(tr_espaco_fisico=espaco)
            .exclude(id__in=recusadas_ids)
            .filter(
                trtransmissaohorario__fim__date__gte=hoje,
                trtransmissaohorario__inicio__date__lte=limite_agenda,
            )
            .values_list("id", flat=True)
            .distinct()
        )

        # Busca todos os horários dessas transmissões (relevantes pro intervalo)
        horarios = TrTransmissaoHorario.objects.filter(
            tr_transmissao_id__in=transmissoes_ids,
            fim__date__gte=hoje,
            inicio__date__lte=limite_agenda,
        ).only("inicio", "fim")

        # Monta o set de datas ocupadas - considera dias pré e pós transmissão
        datas_ocupadas = set()
        for horario in horarios:
            inicio = horario.inicio.date() - timedelta(
                days=espaco.dias_pre_transmissao or 0
            )
            fim = horario.fim.date() + timedelta(days=espaco.dias_pos_transmissao or 0)
            data_atual = inicio
            while data_atual <= fim:
                if hoje <= data_atual <= limite_agenda:
                    datas_ocupadas.add(data_atual)
                data_atual += timedelta(days=1)

        # Inclui dias indisponíveis cadastrados
        indisponiveis = TrIndisponibilidadeEquipe.objects.filter(
            data__gte=hoje, data__lte=limite_agenda
        ).values_list("data", flat=True)
        datas_ocupadas.update(indisponiveis)

        # Mapeia contagem de transmissões por mês já feitas (usando horarios válidos, sem recusadas)
        horarios_validos = (
            TrTransmissaoHorario.objects.exclude(tr_transmissao_id__in=recusadas_ids)
            .filter(
                inicio__date__gte=hoje,
                inicio__date__lte=limite_agenda,
            )
            .values_list("inicio", flat=True)
        )
        contagem_mes = Counter()
        for dt in horarios_validos:
            data = dt.date()
            key = (data.year, data.month)
            contagem_mes[key] += 1

        # Monta lista de datas disponíveis
        datas_validas = []
        data_atual = data_inicial
        while data_atual <= limite_agenda:
            isodow = str(data_atual.isoweekday())  # '1' = segunda, ..., '7' = domingo

            # Testa todas as condições do dia
            if (
                isodow in dias_permitidos
                and data_atual not in datas_ocupadas
                and contagem_mes[(data_atual.year, data_atual.month)]
                < limites.maximo_por_mes
            ):
                datas_validas.append(data_atual.isoformat())
            data_atual += timedelta(days=1)

        return Response(
            DiasDisponiveisSerializer(
                {
                    "inicio_periodo": hoje,
                    "fim_periodo": limite_agenda,
                    "datas_disponiveis": datas_validas,
                }
            ).data
        )

    @extend_schema(**DATAS_DISPONIVEIS_VIEW_DOCS["post"])
    def post(self, request):
        # 1. Pega os valores enviados
        inicio_str = request.data.get("inicio")
        fim_str = request.data.get("fim")

        if not inicio_str or not fim_str:
            raise ValidationError({"detail": ERRO_DATAS_OBRIGATORIAS})

        # 2. Converte para date e valida formato
        try:
            inicio = datetime.fromisoformat(inicio_str).date()
            fim = datetime.fromisoformat(fim_str).date()
        except ValueError:
            raise ValidationError({"detail": ERRO_DATA_FORMATO})

        # 3. Garante que a data final não é menor que a inicial
        if fim < inicio:
            raise ValidationError({"detail": ERRO_DATA_INVALIDA_INICIO_FIM})

        # 4. Busca os limites e calcula data mínima válida
        limites = TrLimites.objects.get(pk=1)
        hoje = timezone.localdate()
        dias_de_antecedencia = hoje + timedelta(days=limites.dias_de_antecedencia)

        # 5. Verificação da antecedência mínima
        if inicio < dias_de_antecedencia:
            raise ValidationError({"detail": ERRO_DATA_INVALIDA_INTERVALO})

        # 6. Busca o espaço físico
        try:
            espaco = TrEspacoFisico.objects.get(id=request.espaco_fisico)
        except TrEspacoFisico.DoesNotExist:
            raise ValidationError({"detail": ERRO_ESPACO_NAO_ENCONTRADO})

        # 7. Dias permitidos pela equipe
        dias_permitidos = set(
            TrDisponibilidadeEquipe.objects.values_list("dia_semana", flat=True)
        )

        # 8. Ocupações existentes (considerando buffers)
        recusadas_ids = TrTransmissaoRecusada.objects.values_list(
            "tr_transmissao_id", flat=True
        )
        transmissoes_ids = (
            TrTransmissao.objects.filter(tr_espaco_fisico=espaco)
            .exclude(id__in=recusadas_ids)
            .values_list("id", flat=True)
        )

        horarios = TrTransmissaoHorario.objects.filter(
            tr_transmissao_id__in=transmissoes_ids,
            fim__date__gte=hoje,
            inicio__date__lte=fim,
        ).only("inicio", "fim")

        # 9. Calcula datas indisponíveis (com buffers de pré/pós)
        datas_indisponiveis = set()
        for horario in horarios:
            inicio_t = horario.inicio.date() - timedelta(
                days=espaco.dias_pre_transmissao or 0
            )
            fim_t = horario.fim.date() + timedelta(
                days=espaco.dias_pos_transmissao or 0
            )
            data_atual = inicio_t
            while data_atual <= fim_t:
                if hoje <= data_atual <= fim:
                    datas_indisponiveis.add(data_atual)
                data_atual += timedelta(days=1)

        # Inclui datas indisponíveis fixas (ex: feriados)
        indisponiveis_fixas = TrIndisponibilidadeEquipe.objects.filter(
            data__gte=inicio, data__lte=fim
        ).values_list("data", flat=True)
        datas_indisponiveis.update(indisponiveis_fixas)

        # 10. Verifica se todas as datas do período são permitidas e livres
        data_atual = inicio
        while data_atual <= fim:
            isodow = str(data_atual.isoweekday())
            if data_atual in datas_indisponiveis:
                raise ValidationError(
                    {"detail": f"{ERRO_DATA_INDISPONIVEL}: ({data_atual.isoformat()})"}
                )
            if isodow not in dias_permitidos:
                raise ValidationError(
                    {"detail": f"{ERRO_DATA_INVALIDA}: ({data_atual.isoformat()})"}
                )
            data_atual += timedelta(days=1)

        # 11. Verifica limite global por mês
        for ano, mes in get_meses_no_intervalo(inicio, fim):
            pedidos_mes = (
                TrTransmissaoHorario.objects.exclude(
                    tr_transmissao_id__in=recusadas_ids
                )
                .filter(
                    inicio__date__year=ano,
                    inicio__date__month=mes,
                )
                .count()
            )
            if pedidos_mes >= limites.maximo_por_mes:
                raise ValidationError({"detail": ERRO_LIMITES_LIMITE_POR_MES})

        # 12. Verifica limite global por semana
        for ano, sem in get_semanas_no_intervalo(inicio, fim):
            pedidos_semana = (
                TrTransmissaoHorario.objects.exclude(
                    tr_transmissao_id__in=recusadas_ids
                )
                .filter(
                    inicio__date__year=ano,
                    inicio__date__week=sem,
                )
                .count()
            )
            if pedidos_semana >= limites.maximo_por_semana:
                raise ValidationError({"detail": ERRO_LIMITES_LIMITE_POR_SEMANA})

        # 13. Verifica máximo de dias por semana
        dias_semana = dias_por_semana(inicio, fim)
        if any(qtd > limites.maximo_dias_na_semana for qtd in dias_semana.values()):
            raise ValidationError({"detail": ERRO_LIMITES_LIMITE_NA_SEMANA})

        # 14. Evento pode atravessar semana?
        if not limites.evento_passando_de_semana and len(dias_semana) > 1:
            raise ValidationError({"detail": ERRO_LIMITES_LIMITE_SEMANA})

        # 15. Se chegou aqui, tudo certo: salva na sessão
        request.session["transmissao_data_inicio"] = inicio_str
        request.session["transmissao_data_inicio_hash"] = gerar_hash(inicio_str)
        request.session["transmissao_data_fim"] = fim_str
        request.session["transmissao_data_fim_hash"] = gerar_hash(fim_str)

        return Response({"detail": OK_PERIODO_SELECIONADO}, status=status.HTTP_200_OK)


class DatasFimValidasAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsRequisitanteTransmissao]

    @extend_schema(**DATAS_FIM_VALIDAS_VIEW_DOCS["get"])
    def get(self, request):
        inicio_str = request.query_params.get("inicio")
        if not inicio_str:
            raise ValidationError({"detail": ERRO_DATA_INVALIDA_INICIO_OBRIGATORIO})

        try:
            inicio = datetime.fromisoformat(inicio_str).date()
        except ValueError:
            raise ValidationError({"detail": ERRO_DATA_INVALIDA})

        limites = TrLimites.objects.get(pk=1)
        hoje = timezone.localdate()
        fim_agenda = hoje + timedelta(days=limites.dias_de_agenda_aberta)

        if inicio < hoje + timedelta(days=limites.dias_de_antecedencia):
            raise ValidationError({"detail": ERRO_DATA_INVALIDA_INICIO})

        try:
            espaco = TrEspacoFisico.objects.get(id=request.session["espaco_fisico"])
        except TrEspacoFisico.DoesNotExist:
            raise ValidationError({"detail": ERRO_ESPACO_NAO_ENCONTRADO})

        dias_permitidos = set(
            TrDisponibilidadeEquipe.objects.values_list("dia_semana", flat=True)
        )

        recusadas_ids = TrTransmissaoRecusada.objects.values_list(
            "tr_transmissao_id", flat=True
        )

        transmissoes_ids = (
            TrTransmissao.objects.filter(tr_espaco_fisico=espaco)
            .exclude(id__in=recusadas_ids)
            .values_list("id", flat=True)
        )

        horarios = TrTransmissaoHorario.objects.filter(
            tr_transmissao_id__in=transmissoes_ids,
            fim__date__gte=inicio,
        ).only("inicio", "fim")

        # 1. Ocupações por buffers de pré/pós
        datas_indisponiveis = set()
        for h in horarios:
            data1 = h.inicio.date() - timedelta(days=espaco.dias_pre_transmissao or 0)
            data2 = h.fim.date() + timedelta(days=espaco.dias_pos_transmissao or 0)
            atual = data1
            while atual <= data2:
                if atual >= inicio:
                    datas_indisponiveis.add(atual)
                atual += timedelta(days=1)

        # 2. Indisponibilidades fixas
        indisponiveis_fixas = TrIndisponibilidadeEquipe.objects.filter(
            data__gte=inicio, data__lte=fim_agenda
        ).values_list("data", flat=True)
        datas_indisponiveis.update(indisponiveis_fixas)

        # 3. Geração da lista de datas finais válidas
        datas_fim_validas = []
        data_fim = inicio
        while data_fim <= fim_agenda:
            isodow = str(data_fim.isoweekday())

            if any(
                dt in datas_indisponiveis or str(dt.isoweekday()) not in dias_permitidos
                for dt in self._intervalo(inicio, data_fim)
            ):
                data_fim += timedelta(days=1)
                continue

            dias_semana = dias_por_semana(inicio, data_fim)
            if any(qtd > limites.maximo_dias_na_semana for qtd in dias_semana.values()):
                break

            if not limites.evento_passando_de_semana and len(dias_semana) > 1:
                break

            if not self._verificar_limites(inicio, data_fim, limites, recusadas_ids):
                break

            datas_fim_validas.append(data_fim.isoformat())
            data_fim += timedelta(days=1)

        return Response({"datas_fim_validas": datas_fim_validas})

    def _intervalo(self, inicio, fim):
        atual = inicio
        while atual <= fim:
            yield atual
            atual += timedelta(days=1)

    def _verificar_limites(self, inicio, fim, limites, recusadas_ids):
        for ano, mes in get_meses_no_intervalo(inicio, fim):
            qtd = (
                TrTransmissaoHorario.objects.exclude(
                    tr_transmissao_id__in=recusadas_ids
                )
                .filter(inicio__date__year=ano, inicio__date__month=mes)
                .count()
            )
            if qtd >= limites.maximo_por_mes:
                return False

        for ano, semana in get_semanas_no_intervalo(inicio, fim):
            qtd = (
                TrTransmissaoHorario.objects.exclude(
                    tr_transmissao_id__in=recusadas_ids
                )
                .filter(inicio__date__year=ano, inicio__date__week=semana)
                .count()
            )
            if qtd >= limites.maximo_por_semana:
                return False

        return True


class HorariosDisponiveisAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsRequisitanteTransmissao]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        aceite = request.session.get("aceite_termo")
        if not aceite:
            raise ValidationError({"detail": ERRO_ACEITE_TERMO_NAO_REALIZADO})

        momento_str = aceite.get("agora")
        hash_armazenado = aceite.get("hash")

        if not momento_str or not hash_armazenado:
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            momento = timezone.datetime.fromisoformat(momento_str)
            if timezone.is_naive(momento):
                momento = timezone.make_aware(momento, timezone.get_current_timezone())
        except Exception:
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        if hash_armazenado != gerar_hash(str(momento)):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        if timezone.now() - momento > timedelta(hours=1):
            raise ValidationError({"detail": ERRO_ACEITE_TERMO_EXPIRADO})

        if "espaco_fisico" not in request.session:
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if "espaco_fisico_hash" not in request.session:
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["espaco_fisico_hash"] != gerar_hash(
            request.session["espaco_fisico"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            espaco = TrEspacoFisico.objects.get(id=request.session["espaco_fisico"])
        except TrEspacoFisico.DoesNotExist:
            raise ValidationError({"detail": ERRO_ESPACO_NAO_ENCONTRADO})

        if "transmissao_data_inicio" not in request.session:
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if "transmissao_data_inicio_hash" not in request.session:
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["transmissao_data_inicio_hash"] != gerar_hash(
            request.session["transmissao_data_inicio"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        if "transmissao_data_fim" not in request.session:
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if "transmissao_data_fim_hash" not in request.session:
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["transmissao_data_fim_hash"] != gerar_hash(
            request.session["transmissao_data_fim"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        request.espaco = espaco
        request.data_inicio = datetime.fromisoformat(
            request.session["transmissao_data_inicio"]
        ).date()
        request.data_fim = datetime.fromisoformat(
            request.session["transmissao_data_fim"]
        ).date()

    @extend_schema(**HORARIOS_DISPONIVEIS_VIEW_DOCS["get"])
    def get(self, request):
        espaco = request.espaco
        data_inicio = request.data_inicio
        data_fim = request.data_fim

        # Dias permitidos (ex: "1" = segunda, ..., "7" = domingo)
        dias_permitidos = set(
            TrDisponibilidadeEquipe.objects.values_list("dia_semana", flat=True)
        )

        # Horários padrão por dia da semana
        horarios_padrao = {}
        for h in TrDisponibilidadeEquipe.objects.all():
            horarios_padrao.setdefault(h.dia_semana, []).append((h.inicio, h.fim))

        # Busca transmissões do espaço físico no intervalo + buffers
        transmissoes_ids = TrTransmissao.objects.filter(
            tr_espaco_fisico=espaco
        ).values_list("id", flat=True)

        # Todas reservas que podem interferir no intervalo
        horarios_reservados = TrTransmissaoHorario.objects.filter(
            tr_transmissao_id__in=transmissoes_ids,
            fim__date__gte=data_inicio
            - timedelta(days=espaco.dias_pre_transmissao or 0),
            inicio__date__lte=data_fim
            + timedelta(days=espaco.dias_pos_transmissao or 0),
        )

        # Indexa reservas por dia
        reservas_por_dia = {}
        for h in horarios_reservados:
            # Aplica buffer de pré/pós
            data_ini = h.inicio.date() - timedelta(
                days=espaco.dias_pre_transmissao or 0
            )
            data_fim_res = h.fim.date() + timedelta(
                days=espaco.dias_pos_transmissao or 0
            )
            data = data_ini
            while data <= data_fim_res:
                reservas_por_dia.setdefault(data, []).append(
                    (h.inicio.time(), h.fim.time())
                )
                data += timedelta(days=1)

        # Gera a lista de dias
        data_atual = data_inicio
        dias_disponiveis = []

        while data_atual <= data_fim:
            isodow = str(data_atual.isoweekday())
            dia_str = data_atual.isoformat()

            if isodow not in dias_permitidos:
                dias_disponiveis.append(
                    {
                        "data": dia_str,
                        "dia_semana": isodow,
                        "horarios": [],
                    }
                )
                data_atual += timedelta(days=1)
                continue

            padroes = horarios_padrao.get(isodow, [])
            reservas = reservas_por_dia.get(data_atual, [])

            horarios_livres = []
            for inicio_padrao, fim_padrao in padroes:
                blocos = [(inicio_padrao, fim_padrao)]
                for res_inicio, res_fim in reservas:
                    novos_blocos = []
                    for b_ini, b_fim in blocos:
                        # Sem interseção
                        if res_fim <= b_ini or res_inicio >= b_fim:
                            novos_blocos.append((b_ini, b_fim))
                        else:
                            # Corta antes
                            if b_ini < res_inicio:
                                novos_blocos.append((b_ini, res_inicio))
                            # Corta depois
                            if res_fim < b_fim:
                                novos_blocos.append((res_fim, b_fim))
                    blocos = novos_blocos
                # Salva blocos finais válidos
                for b_ini, b_fim in blocos:
                    if b_ini < b_fim:
                        horarios_livres.append(
                            {
                                "inicio": b_ini.strftime("%H:%M"),
                                "fim": b_fim.strftime("%H:%M"),
                            }
                        )

            dias_disponiveis.append(
                {
                    "data": dia_str,
                    "dia_semana": isodow,
                    "horarios": horarios_livres,
                }
            )
            data_atual += timedelta(days=1)

        return Response(ListaDiasDisponiveisSerializer({"dias": dias_disponiveis}).data)

    @extend_schema(**HORARIOS_DISPONIVEIS_VIEW_DOCS["post"])
    def post(self, request):
        horarios_selecionados = request.data.get("horarios", [])
        if not horarios_selecionados:
            raise ValidationError({"detail": ERRO_HORARIO_SEM_HORARIO})

        observacao = str(request.data.get("observacao") or "").strip()
        if not observacao:
            raise ValidationError({"detail": ERRO_TRANSMISSAO_OBSERVACAO})

        try:
            data_inicio = datetime.fromisoformat(
                request.session["transmissao_data_inicio"]
            ).date()
            data_fim = datetime.fromisoformat(
                request.session["transmissao_data_fim"]
            ).date()
        except Exception:
            raise ValidationError({"detail": ERRO_DATA_SESSAO})

        espaco = request.espaco

        # Busca transmissões e horários já reservados (com buffers)
        transmissoes_ids = TrTransmissao.objects.filter(
            tr_espaco_fisico=espaco
        ).values_list("id", flat=True)

        horarios_reservados = TrTransmissaoHorario.objects.filter(
            tr_transmissao_id__in=transmissoes_ids,
            fim__date__gte=data_inicio
            - timedelta(days=espaco.dias_pre_transmissao or 0),
            inicio__date__lte=data_fim
            + timedelta(days=espaco.dias_pos_transmissao or 0),
        )

        # Indexa reservas por data para validação rápida
        reservas_por_data = {}
        for h in horarios_reservados:
            reservas_por_data.setdefault(h.inicio.date(), []).append(
                (h.inicio.time(), h.fim.time())
            )

        # Valida cada horário enviado
        horarios_validos = []
        for item in horarios_selecionados:
            data_str = item.get("data")
            h_ini = item.get("inicio")
            h_fim = item.get("fim")

            if not (data_str and h_ini and h_fim):
                raise ValidationError(
                    {"detail": f"{ERRO_HORARIO_INFORMACOES_INCOMPLETAS} {item}"}
                )

            try:
                data_dia = datetime.fromisoformat(data_str).date()
                hora_ini = datetime.strptime(h_ini, "%H:%M").time()
                hora_fim = datetime.strptime(h_fim, "%H:%M").time()
            except Exception:
                raise ValidationError(
                    {"detail": f"{ERRO_HORARIO_FORMATO_INVALIDO} {item}"}
                )

            if data_dia < data_inicio or data_dia > data_fim:
                raise ValidationError(
                    {"detail": f"{ERRO_DATA_INVALIDA_INTERVALO}: {data_str}"}
                )

            if hora_ini >= hora_fim:
                raise ValidationError(
                    {"detail": f"{ERRO_HORARIO_INVALIDO_INICIO_FIM}: {data_str}"}
                )

            # Valida se está dentro da baliza da equipe
            isodow = str(data_dia.isoweekday())
            balizas = TrDisponibilidadeEquipe.objects.filter(dia_semana=isodow)
            dentro_de_alguma_baliza = any(
                to_naive_time(baliza.inicio) <= hora_ini
                and hora_fim <= to_naive_time(baliza.fim)
                for baliza in balizas
            )
            if not dentro_de_alguma_baliza:
                raise ValidationError(
                    {
                        "detail": f"{data_str} - {h_ini}-{h_fim}: {ERRO_HORARIO_NAO_PERMITIDO}"
                    }
                )

            # Valida se o horário não conflita com reservas já existentes (no mesmo dia)
            reservas_no_dia = reservas_por_data.get(data_dia, [])
            conflito = False
            for res_ini, res_fim in reservas_no_dia:
                if not (hora_fim <= res_ini or hora_ini >= res_fim):
                    conflito = True
                    break
            if conflito:
                raise ValidationError(
                    {
                        "detail": f"{data_str} - {h_ini}-{h_fim}: {ERRO_HORARIO_CONFLITO_RESERVA}"
                    }
                )

            horarios_validos.append(
                {
                    "data": data_str,
                    "inicio": h_ini,
                    "fim": h_fim,
                }
            )

        if not horarios_validos:
            raise ValidationError({"detail": ERRO_HORARIO_SEM_HORARIO})

        termo = TrTermo.objects.order_by("-id").first()
        if not termo:
            raise ValidationError({"detail": ERRO_GET_TERMO_SEM_TERMO})

        try:
            # Cria o pedido de transmissão "principal" (sem campos de hora)
            transmissao = TrTransmissao.objects.create(
                tr_termo=termo,
                tr_espaco_fisico=espaco,
                cm_pessoa=CmPessoa.objects.get(cpf=request.user.username),
                observacao=observacao,
            )
            # Salva todos os horários do pedido
            for h in horarios_validos:
                inicio_h = timezone.make_aware(
                    datetime.fromisoformat(f"{h['data']}T{h['inicio']}"),
                    timezone.get_current_timezone(),
                )
                fim_h = timezone.make_aware(
                    datetime.fromisoformat(f"{h['data']}T{h['fim']}"),
                    timezone.get_current_timezone(),
                )
                TrTransmissaoHorario.objects.create(
                    tr_transmissao=transmissao,
                    inicio=inicio_h,
                    fim=fim_h,
                )
        except Exception as e:
            raise ValidationError({"detail": f"{ERRO_TRANSMISSAO_SALVAR}: {str(e)}"})

        request.session.flush()
        request.session["transmissao"] = {
            "id": transmissao.id,
            "hash": gerar_hash(str(transmissao.id)),
        }

        return Response(
            {"detail": OK_HORARIO_SELECIONADO, "id": transmissao.id},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(**CONFIRMACAO_TRANSMISSAO_VIEW_DOCS["get"])
class ConfirmacaoTransmissaoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsRequisitanteTransmissao]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        transmissao_sessao = request.session.get("transmissao")
        if not transmissao_sessao:
            raise ValidationError({"detail": ERRO_TRANSMISSAO_SESSAO})

        transmissao_id = transmissao_sessao.get("id")
        hash_armazenado = transmissao_sessao.get("hash")

        if not transmissao_id or not hash_armazenado:
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        if hash_armazenado != gerar_hash(str(transmissao_id)):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            transmissao = TrTransmissao.objects.get(id=transmissao_id)
        except TrTransmissao.DoesNotExist:
            raise ValidationError({"detail": ERRO_TRANSMISSAO_NAO_ENCONTRADA})

        request.transmissao = transmissao

    def get(self, request):
        confirmacao = TransmissaoConfirmacaoSerializer(request.transmissao).data
        confirmacao["assinatura"] = hash_transmissao(request.transmissao)

        request.session.flush()

        horarios_str = "\n".join(
            f"- {formatar_horario(h['inicio'], h['fim'])}"
            for h in confirmacao["horarios"]
        )

        assunto = f"{EMAIL_TRANSMISSAO_ASSUNTO}"
        mensagem = (
            f"Requisitante: {confirmacao['requisitante_nome']}\n"
            f"CPF: ({confirmacao['requisitante_cpf']})\n"
            f"E-mail: {confirmacao['requisitante_email']}\n"
            f"Espaço físico: {confirmacao['espaco_fisico']}\n"
            f"Horários:\n{horarios_str}\n"
            f"Observação: {confirmacao['observacao']}\n"
            f"Assinatura digital: {confirmacao['assinatura']}\n\n"
            f"{EMAIL_ENDERECO_NAO_MONITORADO}\n"
            f"{EMAIL_DUVIDAS_PARA_O_SUPORTE} {INFO_ENTRE_CONTATO_SUPORTE}\n"
            f"{EMAIL_ASSINATURA}"
        )

        emails_to = []
        emails_cc = []
        emails_cco = []
        for e in TrTransmissaoEmail.objects.all():
            if e.tipo_email_envio == "cc":
                emails_cc.append(e.email)
            elif e.tipo_email_envio == "cco":
                emails_cco.append(e.email)
            else:
                emails_to.append(e.email)

        # Se não houver TO, pelo menos um CCO (padrão seguro)
        if not emails_to:
            emails_to = emails_cco or emails_cc

        email = EmailMessage(
            subject=assunto,
            body=mensagem,
            from_email=EMAIL_HOST_USER,
            to=emails_to,
            cc=emails_cc,
            bcc=emails_cco,
        )
        email.send(fail_silently=False)

        return Response(confirmacao)
