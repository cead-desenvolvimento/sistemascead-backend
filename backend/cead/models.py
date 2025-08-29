import hashlib
from urllib.parse import urlencode

from pytz import timezone

from django.contrib.auth.models import Group
from django.db import models
from django.urls import reverse
from django.utils import timezone as tz

# Para AcPoloHorarioFuncionamento e TrHorarioTransmissao
DIAS_SEMANA = (
    ("1", "Segunda-feira"),
    ("2", "Terça-feira"),
    ("3", "Quarta-feira"),
    ("4", "Quinta-feira"),
    ("5", "Sexta-feira"),
    ("6", "Sábado"),
    ("7", "Domingo"),
)


class AcCurso(models.Model):
    id = models.BigAutoField(primary_key=True)
    ac_curso_tipo = models.ForeignKey(
        "AcCursoTipo", models.DO_NOTHING, verbose_name="Tipo de curso"
    )
    cm_pessoa_coordenador = models.ForeignKey(
        "CmPessoa", models.DO_NOTHING, blank=True, null=True, verbose_name="Coordenador"
    )
    nome = models.CharField(max_length=127)
    email = models.CharField(max_length=127, blank=True, null=True)
    ativo = models.BooleanField()
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    perfil_egresso = models.TextField(
        blank=True, null=True, verbose_name="Perfil do egresso"
    )
    ddd = models.CharField(max_length=2, blank=True, null=True, verbose_name="DDD")
    telefone = models.CharField(max_length=9, blank=True, null=True)

    def __str__(self):
        return self.nome

    def telefone_formatado(self):
        if self.ddd and self.telefone:
            telefone = self.telefone.strip()
            if len(telefone) == 9:
                return f"({self.ddd}) {telefone[:3]} {telefone[3:6]} {telefone[6:]}"
            elif len(telefone) == 8:
                return f"({self.ddd}) {telefone[:4]} {telefone[4:]}"
            else:
                return f"({self.ddd}) {telefone}"
        return "-"

    class Meta:
        verbose_name = "(Acadêmico) Curso"
        verbose_name_plural = "(Acadêmico) Cursos"
        managed = False
        db_table = "ac_curso"


class AcCursoOferta(models.Model):
    id = models.BigAutoField(primary_key=True)
    ac_curso = models.ForeignKey(AcCurso, models.DO_NOTHING, verbose_name="Curso")
    numero = models.SmallIntegerField(
        blank=True,
        null=True,
        db_comment="O numero da oferta, para controle do financeiro",
        verbose_name="Número da oferta",
    )
    inicio_sisuab = models.DateField(
        blank=True, null=True, verbose_name="Data de início no SISUAB"
    )
    inicio = models.DateField(blank=True, null=True)
    fim = models.DateField(blank=True, null=True)
    vagas = models.SmallIntegerField(blank=True, null=True)

    def __str__(self):
        curso_nome = self.ac_curso.nome if self.ac_curso else "-"
        return f"Oferta {self.numero} do curso {curso_nome}"

    class Meta:
        verbose_name = "(Acadêmico) Curso - oferta"
        verbose_name_plural = "(Acadêmico) Cursos - ofertas"
        managed = False
        db_table = "ac_curso_oferta"


class AcCursoOfertaPolo(models.Model):
    id = models.BigAutoField(primary_key=True)
    ac_curso_oferta = models.ForeignKey(
        AcCursoOferta, models.DO_NOTHING, blank=True, null=True, verbose_name="Curso"
    )
    ac_polo = models.ForeignKey("AcPolo", models.DO_NOTHING, verbose_name="Polo")
    vagas = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "(Acadêmico) Curso - oferta - polo"
        verbose_name_plural = "(Acadêmico) Cursos - ofertas - polos"
        managed = False
        db_table = "ac_curso_oferta_polo"


class AcCursoTipo(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=31)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "(Acadêmico) Tipo de curso"
        verbose_name_plural = "(Acadêmico) Tipos de curso"
        managed = False
        db_table = "ac_curso_tipo"


class AcDisciplina(models.Model):
    id = models.BigAutoField(primary_key=True)
    ac_curso = models.ForeignKey(
        AcCurso, models.DO_NOTHING, blank=True, null=True, verbose_name="Curso"
    )
    periodo = models.SmallIntegerField(blank=True, null=True, verbose_name="Período")
    nome = models.CharField(max_length=127)
    codigo = models.CharField(
        max_length=15, blank=True, null=True, verbose_name="Código"
    )
    carga_horaria = models.SmallIntegerField(
        blank=True, null=True, verbose_name="Carga horária"
    )
    ativa = models.BooleanField(verbose_name="Ativa?")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "(Acadêmico) Disciplina"
        verbose_name_plural = "(Acadêmico) Disciplinas"
        managed = False
        db_table = "ac_disciplina"


class AcMantenedor(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=63)
    responsavel = models.CharField(max_length=63, verbose_name="Responsável")
    cnpj = models.CharField(max_length=14, verbose_name="CNPJ")
    email = models.CharField(max_length=63)
    tipo = models.CharField(max_length=10)
    ddd = models.CharField(max_length=2, blank=True, null=True, verbose_name="DDD")
    telefone = models.CharField(max_length=9, blank=True, null=True)
    logradouro = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=63, blank=True, null=True)
    bairro = models.CharField(max_length=63, blank=True, null=True)
    cep = models.CharField(max_length=8, blank=True, null=True)
    cm_municipio = models.ForeignKey(
        "CmMunicipio",
        models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Município",
    )

    def __str__(self):
        if self.nome:
            return self.nome
        return "-"

    def cnpj_formatado(self):
        if self.cnpj:
            return f"{self.cnpj[:2]}.{self.cnpj[2:5]}.{self.cnpj[5:8]}/{self.cnpj[8:12]}-{self.cnpj[12:]}"
        return "-"

    def cep_formatado(self):
        if self.cep and len(self.cep) == 8:
            return f"{self.cep[:5]}-{self.cep[5:]}"
        return self.cep

    class Meta:
        verbose_name = "(Acadêmico) Mantenedor"
        verbose_name_plural = "(Acadêmico) Mantenedores"
        managed = False
        db_table = "ac_mantenedor"


class AcPolo(models.Model):
    id = models.BigAutoField(primary_key=True)
    ac_mantenedor = models.ForeignKey(
        AcMantenedor,
        models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Mantenedor",
    )
    cm_pessoa_coordenador = models.ForeignKey(
        "CmPessoa", models.DO_NOTHING, blank=True, null=True, verbose_name="Coordenador"
    )
    nome = models.CharField(max_length=63)
    email = models.CharField(max_length=63)
    ativo = models.BooleanField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    apresentacao = models.TextField(blank=True, null=True, verbose_name="Apresentação")
    ddd = models.CharField(max_length=2, blank=True, null=True, verbose_name="DDD")
    telefone = models.CharField(max_length=9, blank=True, null=True)
    logradouro = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(
        max_length=10, blank=True, null=True, verbose_name="Número"
    )
    complemento = models.CharField(max_length=63, blank=True, null=True)
    bairro = models.CharField(max_length=127, blank=True, null=True)
    cep = models.CharField(max_length=8, blank=True, null=True, verbose_name="CEP")
    cm_municipio = models.ForeignKey(
        "CmMunicipio",
        models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Município",
    )

    def __str__(self):
        return self.nome

    def cep_formatado(self):
        if self.cep and len(self.cep) == 8:
            return f"{self.cep[:5]}-{self.cep[5:]}"
        return self.cep

    def telefone_formatado(self):
        if self.ddd and self.telefone:
            telefone = self.telefone.strip()
            if len(telefone) == 9:
                return f"({self.ddd}) {telefone[:3]} {telefone[3:6]} {telefone[6:]}"
            elif len(telefone) == 8:
                return f"({self.ddd}) {telefone[:4]} {telefone[4:]}"
            else:
                return f"({self.ddd}) {telefone}"
        return "-"

    class Meta:
        verbose_name = "(Acadêmico) Polo"
        verbose_name_plural = "(Acadêmico) Polos"
        managed = False
        db_table = "ac_polo"


class AcPoloHorarioFuncionamento(models.Model):
    id = models.BigAutoField(primary_key=True)
    ac_polo = models.ForeignKey(AcPolo, models.DO_NOTHING)
    dia_semana = models.CharField(
        max_length=1,
        choices=DIAS_SEMANA,
        db_comment="isodow() do pgsql",
        verbose_name="Dia da semana",
    )
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    class Meta:
        verbose_name = "(Acadêmico) Horário de funcionamento do polo"
        verbose_name_plural = "(Acadêmico) Horários de funcionamento dos polos"
        managed = False
        db_table = "ac_polo_horario_funcionamento"


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = "auth_group"


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey("AuthPermission", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_group_permissions"
        unique_together = (("group", "permission"),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey("DjangoContentType", models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "auth_permission"
        unique_together = (("content_type", "codename"),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "auth_user"


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_user_groups"
        unique_together = (("user", "group"),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_user_user_permissions"
        unique_together = (("user", "permission"),)


class CmPessoaEndereco(models.Model):
    id = models.BigAutoField(primary_key=True)
    cm_pessoa = models.ForeignKey(
        "CmPessoa", models.DO_NOTHING, blank=True, null=True, verbose_name="Pessoa"
    )
    cep = models.CharField(max_length=8, blank=False)
    logradouro = models.CharField(max_length=255, blank=False)
    numero = models.CharField(max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=63, blank=True, null=True)
    bairro = models.CharField(max_length=127, blank=False)
    cm_municipio = models.ForeignKey(
        "CmMunicipio", on_delete=models.DO_NOTHING, blank=False, null=False
    )

    def cep_formatado(self):
        if self.cep and len(self.cep) == 8:
            return f"{self.cep[:5]}-{self.cep[5:]}"
        return self.cep

    class Meta:
        verbose_name = "(Comum) Pessoa - endereço"
        verbose_name_plural = "(Comum) Pessoas - endereços"
        managed = False
        db_table = "cm_pessoa_endereco"


class CmFormacao(models.Model):
    id = models.BigAutoField(primary_key=True)
    cm_titulacao = models.ForeignKey(
        "CmTitulacao", models.DO_NOTHING, verbose_name="Titulação"
    )
    nome = models.CharField(max_length=255)

    def __str__(self):
        return (
            f"{self.cm_titulacao} em {self.nome}"
            if self.nome and self.cm_titulacao
            else "-"
        )

    @classmethod
    def get_formacoes(cls):
        return list(
            cls.objects.values("id", "nome", "cm_titulacao__nome").order_by("nome")
        )

    class Meta:
        verbose_name = "(Comum) Formação"
        verbose_name_plural = "(Comum) Formações"
        managed = False
        db_table = "cm_formacao"


class DjUri(models.Model):
    id = models.BigAutoField(primary_key=True)
    uri = models.CharField(max_length=255, verbose_name="URI")
    descricao = models.TextField(verbose_name="Descrição")

    def __str__(self):
        return self.uri

    class Meta:
        verbose_name = "(Django) URI do frontend"
        verbose_name_plural = "(Django) URIs do frontend"
        managed = False
        db_table = "dj_uri"


class DjGrupoUri(models.Model):
    id = models.BigAutoField(primary_key=True)
    auth_group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        db_constraint=True,  # Mantém a FK mesmo cross-schema
        verbose_name="Grupo",
    )
    dj_uri = models.ForeignKey(DjUri, models.DO_NOTHING, verbose_name="URI")

    class Meta:
        verbose_name = "(Django) Associação grupo Django/URI acessível"
        verbose_name_plural = "(Django) Associações grupos Django/URIs acessíveis"
        managed = False
        db_table = "dj_authgroup_uri"
        unique_together = (("auth_group", "dj_uri"),)


class CmMunicipio(models.Model):
    id = models.BigAutoField(primary_key=True)
    cm_uf = models.ForeignKey("CmUf", models.DO_NOTHING)
    municipio = models.CharField(max_length=31, verbose_name="Município")

    def __str__(self):
        return self.municipio

    def get_municipio_uf(self):
        if self.municipio and self.cm_uf:
            return f"{self.municipio}, {self.cm_uf}"

    class Meta:
        verbose_name = "(Comum) Município"
        verbose_name_plural = "(Comum) Municípios"
        managed = False
        db_table = "cm_municipio"


class CmPessoa(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    cpf = models.CharField(unique=True, max_length=11)
    email = models.CharField(max_length=127)

    def cpf_com_pontos_e_traco(self):
        if self.cpf and len(self.cpf) == 11:
            return f"{self.cpf[:3]}.{self.cpf[3:6]}.{self.cpf[6:9]}-{self.cpf[9:]}"
        return self.cpf

    def __str__(self):
        return f"{self.nome} {self.cpf_com_pontos_e_traco()}"

    class Meta:
        verbose_name = "(Comum) Pessoa"
        verbose_name_plural = "(Comum) Pessoas"
        managed = False
        db_table = "cm_pessoa"


class CmPessoaBanco(models.Model):
    id = models.BigAutoField(primary_key=True)
    cm_pessoa = models.ForeignKey(CmPessoa, models.DO_NOTHING)
    codigo_banco = models.SmallIntegerField()
    agencia = models.SmallIntegerField()
    conta = models.BigIntegerField()
    digito_verificador_conta = models.SmallIntegerField()

    class Meta:
        verbose_name = "(Comum) Pessoa - banco"
        verbose_name_plural = "(Comum) Pessoas - bancos"
        managed = False
        db_table = "cm_pessoa_banco"


class CmPessoaTelefone(models.Model):
    id = models.BigAutoField(primary_key=True)
    cm_pessoa = models.ForeignKey(CmPessoa, models.DO_NOTHING)
    ddd = models.CharField(max_length=2)
    numero = models.CharField(max_length=9)

    def __str__(self):
        if self.ddd and self.numero:
            numero = self.numero.strip()
            if len(numero) == 9:
                return f"({self.ddd}) {numero[:3]} {numero[3:6]} {numero[6:]}"
            elif len(numero) == 8:
                return f"({self.ddd}) {numero[:4]} {numero[4:]}"
            else:
                return f"({self.ddd}) {numero}"
        return "-"

    class Meta:
        verbose_name = "(Comum) Pessoa - telefone"
        verbose_name_plural = "(Comum) Pessoas - telefones"
        managed = False
        db_table = "cm_pessoa_telefone"


class CmTitulacao(models.Model):
    id = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=63)

    def __str__(self):
        if self.nome:
            return self.nome
        return "-"

    class Meta:
        verbose_name = "(Comum) Titulação"
        verbose_name_plural = "(Comum) Titulações"
        managed = False
        db_table = "cm_titulacao"


class CmUf(models.Model):
    id = models.BigAutoField(primary_key=True)
    sigla = models.CharField(max_length=2)
    uf = models.CharField(max_length=20)

    def __str__(self):
        if self.uf:
            return self.uf
        return "-"

    class Meta:
        verbose_name = "(Comum) Unidade da Federação"
        verbose_name_plural = "(Comum) Unidades da Federação"
        managed = False
        db_table = "cm_uf"


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey(
        "DjangoContentType", models.DO_NOTHING, blank=True, null=True
    )
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "django_admin_log"


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "django_content_type"
        unique_together = (("app_label", "model"),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "django_migrations"


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "django_session"


class EdCampo(models.Model):
    id = models.BigAutoField(primary_key=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.descricao:
            return self.descricao
        return "-"

    class Meta:
        verbose_name = "(Editais) Rótulo do edital"
        verbose_name_plural = "(Editais) Rótulos dos editais"
        managed = False
        db_table = "ed_campo"


class EdCota(models.Model):
    id = models.BigAutoField(primary_key=True)
    cota = models.CharField(max_length=63)

    def __str__(self):
        if self.cota:
            return self.cota
        return "-"

    class Meta:
        verbose_name = "(Editais) Tipo de cota"
        verbose_name_plural = "(Editais) Tipos de cotas"
        managed = False
        db_table = "ed_cota"


class EdEdital(models.Model):
    id = models.BigAutoField(primary_key=True)
    numero = models.SmallIntegerField(verbose_name="Número")
    ano = models.SmallIntegerField()
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ac_curso = models.ForeignKey(
        AcCurso, models.DO_NOTHING, blank=True, null=True, verbose_name="Curso"
    )
    data_inicio_inscricao = models.DateTimeField(
        blank=True, null=True, verbose_name="Data e hora de início das inscrições"
    )
    data_fim_inscricao = models.DateTimeField(
        blank=True, null=True, verbose_name="Data e hora de fim das inscrições"
    )
    data_inicio_validacao = models.DateTimeField(
        blank=True, null=True, verbose_name="Data e hora de início da validação"
    )
    data_fim_validacao = models.DateTimeField(
        blank=True, null=True, verbose_name="Data e hora de fim da validação"
    )
    data_validade = models.DateTimeField(
        blank=True, null=True, verbose_name="Data de validade do edital"
    )
    data_cadastro = models.DateTimeField(default=tz.now, blank=True, null=True)
    multiplas_inscricoes = models.BooleanField(
        blank=True, null=True, verbose_name="Permite múltiplas inscrições?"
    )

    def __str__(self):
        if self.descricao:
            return f"{self.numero_ano_edital()} - {self.descricao}"
        return "-"

    def numero_ano_edital(self):
        return f"{self.numero}/{self.ano}"

    class Meta:
        verbose_name = "(Editais) Edital"
        verbose_name_plural = "(Editais) Editais"
        managed = False
        db_table = "ed_edital"


class EdEditalPessoa(models.Model):
    id = models.BigAutoField(primary_key=True)
    cm_pessoa = models.ForeignKey(
        CmPessoa, on_delete=models.DO_NOTHING, verbose_name="Pessoa"
    )
    ed_edital = models.ForeignKey(
        EdEdital, on_delete=models.DO_NOTHING, verbose_name="Edital"
    )

    class Meta:
        verbose_name = "(Editais) Associação de edital e pessoa"
        verbose_name_plural = "(Editais) Associações de editais e pessoas"
        managed = False
        db_table = "ed_edital_pessoa"
        unique_together = (("cm_pessoa", "ed_edital"),)

    def __str__(self):
        return f"{self.ed_edital} - {self.cm_pessoa}"


class EdPessoaFormacao(models.Model):
    id = models.BigAutoField(primary_key=True)
    cm_pessoa = models.ForeignKey(CmPessoa, models.DO_NOTHING, verbose_name="Nome")
    cm_formacao = models.ForeignKey(
        CmFormacao, models.DO_NOTHING, verbose_name="Titulação"
    )
    inicio = models.DateField()
    fim = models.DateField()

    class Meta:
        verbose_name = "(Editais) Formação da pessoa"
        verbose_name_plural = "(Editais) Formações das pessoas"
        managed = False
        db_table = "ed_pessoa_formacao"


class EdPessoaVagaCampoCheckbox(models.Model):
    id = models.BigAutoField(primary_key=True)
    cm_pessoa = models.ForeignKey(CmPessoa, models.DO_NOTHING)
    ed_vaga_campo_checkbox = models.ForeignKey("EdVagaCampoCheckbox", models.DO_NOTHING)

    class Meta:
        verbose_name = "(Editais) Marcação de checkbox pela pessoa"
        verbose_name_plural = "(Editais) Marcações de checkboxes pelas pessoas"
        managed = False
        db_table = "ed_pessoa_vaga_campo_checkbox"


class EdPessoaVagaCampoCombobox(models.Model):
    id = models.BigAutoField(primary_key=True)
    cm_pessoa = models.ForeignKey(CmPessoa, models.DO_NOTHING)
    ed_vaga_campo_combobox = models.ForeignKey("EdVagaCampoCombobox", models.DO_NOTHING)

    class Meta:
        verbose_name = "(Editais) Marcação de combobox pela pessoa"
        verbose_name_plural = "(Editais) Marcações de comboboxes pelas pessoas"
        managed = False
        db_table = "ed_pessoa_vaga_campo_combobox"


class EdPessoaVagaCampoDatebox(models.Model):
    id = models.BigAutoField(primary_key=True)
    cm_pessoa = models.ForeignKey(CmPessoa, models.DO_NOTHING)
    ed_vaga_campo_datebox = models.ForeignKey("EdVagaCampoDatebox", models.DO_NOTHING)

    class Meta:
        verbose_name = "(Editais) Marcação de datebox pela pessoa"
        verbose_name_plural = "(Editais) Marcações de dateboxes pelas pessoas"
        managed = False
        db_table = "ed_pessoa_vaga_campo_datebox"


class EdPessoaVagaCampoCheckboxUpload(models.Model):
    id = models.BigAutoField(primary_key=True)
    ed_pessoa_vaga_campo_checkbox = models.ForeignKey(
        "EdPessoaVagaCampoCheckbox", models.DO_NOTHING
    )
    caminho_arquivo = models.CharField(max_length=511)
    validado = models.BooleanField()

    class Meta:
        verbose_name = "(Editais) Arquivo do candidato - checkbox"
        verbose_name_plural = "(Editais) Arquivos dos candidatos - checkboxes"
        managed = False
        db_table = "ed_pessoa_vaga_campo_checkbox_upload"

    # Cria a URL para baixar o arquivo utilizando x-accel-redirect
    @property
    def url_download(self):
        return f"{reverse('baixar_arquivo')}?{urlencode({'caminho': self.caminho_arquivo})}"

    @property
    def url_download_inscricao(self):
        return f"{reverse('baixar_arquivo_inscricao')}?{urlencode({'caminho': self.caminho_arquivo})}"


class EdPessoaVagaCampoComboboxUpload(models.Model):
    id = models.BigAutoField(primary_key=True)
    ed_pessoa_vaga_campo_combobox = models.ForeignKey(
        "EdPessoaVagaCampoCombobox", models.DO_NOTHING
    )
    caminho_arquivo = models.CharField(max_length=511)
    validado = models.BooleanField()

    class Meta:
        verbose_name = "(Editais) Arquivo do candidato - combobox"
        verbose_name_plural = "(Editais) Arquivos dos candidatos - comboboxes"
        managed = False
        db_table = "ed_pessoa_vaga_campo_combobox_upload"

    @property
    def url_download(self):
        return f"{reverse('baixar_arquivo')}?{urlencode({'caminho': self.caminho_arquivo})}"

    @property
    def url_download_inscricao(self):
        return f"{reverse('baixar_arquivo_inscricao')}?{urlencode({'caminho': self.caminho_arquivo})}"


class EdPessoaVagaCampoDateboxUpload(models.Model):
    id = models.BigAutoField(primary_key=True)
    ed_pessoa_vaga_campo_datebox = models.ForeignKey(
        "EdPessoaVagaCampoDatebox", models.DO_NOTHING
    )
    caminho_arquivo = models.CharField(max_length=511)
    validado = models.BooleanField()

    class Meta:
        verbose_name = "(Editais) Arquivo do candidato - datebox"
        verbose_name_plural = "(Editais) Arquivos dos candidatos - dateboxes"
        managed = False
        db_table = "ed_pessoa_vaga_campo_datebox_upload"

    @property
    def url_download(self):
        return f"{reverse('baixar_arquivo')}?{urlencode({'caminho': self.caminho_arquivo})}"

    @property
    def url_download_inscricao(self):
        return f"{reverse('baixar_arquivo_inscricao')}?{urlencode({'caminho': self.caminho_arquivo})}"


class EdPessoaVagaCampoCheckboxPontuacao(models.Model):
    id = models.BigAutoField(primary_key=True)
    ed_pessoa_vaga_campo_checkbox = models.ForeignKey(
        "EdPessoaVagaCampoCheckbox",
        models.DO_NOTHING,
        related_name="pontuacoes",
    )
    pontuacao = models.FloatField(verbose_name="Pontuação")

    class Meta:
        verbose_name = "(Editais) Pontuação do candidato - checkbox"
        verbose_name_plural = "(Editais) Pontuações dos candidatos - checkboxes"
        managed = False
        db_table = "ed_pessoa_vaga_campo_checkbox_pontuacao"


class EdPessoaVagaCampoComboboxPontuacao(models.Model):
    id = models.BigAutoField(primary_key=True)
    ed_pessoa_vaga_campo_combobox = models.ForeignKey(
        "EdPessoaVagaCampoCombobox",
        models.DO_NOTHING,
        related_name="pontuacoes",
    )
    pontuacao = models.FloatField(verbose_name="Pontuação")

    class Meta:
        verbose_name = "(Editais) Pontuação do candidato - combobox"
        verbose_name_plural = "(Editais) Pontuações dos candidatos - comboboxes"
        managed = False
        db_table = "ed_pessoa_vaga_campo_combobox_pontuacao"


class EdPessoaVagaCampoDateboxPontuacao(models.Model):
    id = models.BigAutoField(primary_key=True)
    ed_pessoa_vaga_campo_datebox = models.ForeignKey(
        "EdPessoaVagaCampoDatebox",
        models.DO_NOTHING,
        related_name="pontuacoes",
    )
    pontuacao = models.FloatField(verbose_name="Pontuação")

    class Meta:
        verbose_name = "(Editais) Pontuação do candidato - datebox"
        verbose_name_plural = "(Editais) Pontuações dos candidatos - dateboxes"
        managed = False
        db_table = "ed_pessoa_vaga_campo_datebox_pontuacao"


class EdPessoaVagaCampoDateboxPeriodo(models.Model):
    id = models.BigAutoField(primary_key=True)
    ed_pessoa_vaga_campo_datebox = models.ForeignKey(
        EdPessoaVagaCampoDatebox,
        models.DO_NOTHING,
        related_name="periodos",
    )
    inicio = models.DateField(verbose_name="Início")
    fim = models.DateField(verbose_name="Fim")

    class Meta:
        verbose_name = "(Editais) Período (informado) do candidato - datebox"
        verbose_name_plural = (
            "(Editais) Períodos (informados) dos candidatos - dateboxes"
        )
        managed = False
        db_table = "ed_pessoa_vaga_campo_datebox_periodo"


class EdPessoaVagaConfirmacao(models.Model):
    id = models.BigAutoField(primary_key=True)
    cm_pessoa = models.ForeignKey(CmPessoa, models.DO_NOTHING)
    ed_vaga = models.ForeignKey("EdVaga", models.DO_NOTHING)

    class Meta:
        verbose_name = "(Editais) Pessoa confirmada"
        verbose_name_plural = "(Editais) Pessoas confirmadas"
        managed = False
        db_table = "ed_pessoa_vaga_confirmacao"


class EdPessoaVagaCota(models.Model):
    id = models.BigAutoField(primary_key=True)
    cm_pessoa = models.ForeignKey(CmPessoa, models.DO_NOTHING)
    ed_vaga_cota = models.ForeignKey("EdVagaCota", models.DO_NOTHING)

    class Meta:
        verbose_name = "(Editais) Associação entre pessoa, vaga e cota"
        verbose_name_plural = "(Editais) Associações entre pessoas, vagas e cotas"
        managed = False
        db_table = "ed_pessoa_vaga_cota"
        unique_together = (("cm_pessoa", "ed_vaga_cota"),)


class EdPessoaVagaInscricao(models.Model):
    id = models.BigAutoField(primary_key=True)
    cm_pessoa = models.ForeignKey(CmPessoa, models.DO_NOTHING, verbose_name="Nome")
    ed_vaga = models.ForeignKey("EdVaga", models.DO_NOTHING, verbose_name="Vaga")
    pontuacao = models.SmallIntegerField(
        blank=True, null=True, verbose_name="Pontuação"
    )
    data = models.DateTimeField(verbose_name="Data da inscrição")

    class Meta:
        verbose_name = "(Editais) Pessoa inscrita"
        verbose_name_plural = "(Editais) Pessoas inscritas"
        managed = False
        db_table = "ed_pessoa_vaga_inscricao"

    # Cria uma 'assinatura' para a inscricao da pessoa e evitar alteracao de dados
    def codigo_pessoavagainscricao(self):
        pontuacao_str = str(self.pontuacao) if self.pontuacao is not None else "0"
        return hashlib.sha256(
            f"{self.id}{self.cm_pessoa_id}{self.ed_vaga_id}{pontuacao_str}{self.data}".encode()
        ).hexdigest()

    codigo_pessoavagainscricao.short_description = "Código gerado na inscrição"


class EdPessoaVagaGerouFicha(models.Model):
    id = models.BigAutoField(primary_key=True)
    ed_pessoa_vaga_validacao = models.ForeignKey(
        "EdPessoaVagaValidacao", models.DO_NOTHING
    )

    class Meta:
        verbose_name = "(Editais) Pessoa - gerou ficha?"
        verbose_name_plural = "(Editais) Pessoas - geraram fichas?"
        managed = False
        db_table = "ed_pessoa_vaga_gerouficha"


class EdPessoaVagaJustificativa(models.Model):
    id = models.BigAutoField(primary_key=True)
    cm_pessoa = models.ForeignKey(CmPessoa, models.DO_NOTHING)
    cm_pessoa_responsavel_justificativa = models.ForeignKey(
        CmPessoa,
        models.DO_NOTHING,
        related_name="edpessoavagajustificativa_cm_pessoa_responsavel_justificativa_set",
        null=True,
        blank=True,
    )
    ed_vaga = models.ForeignKey("EdVaga", models.DO_NOTHING)
    justificativa = models.TextField()

    class Meta:
        verbose_name = "(Editais) Pessoa - justificativa"
        verbose_name_plural = "(Editais) Pessoas - justificativas"
        managed = False
        db_table = "ed_pessoa_vaga_justificativa"

    def __str__(self):
        if self.justificativa:
            return self.justificativa
        return "-"


class EdPessoaVagaValidacao(models.Model):
    id = models.BigAutoField(primary_key=True)
    cm_pessoa = models.ForeignKey(CmPessoa, models.DO_NOTHING, verbose_name="Nome")
    cm_pessoa_responsavel_validacao = models.ForeignKey(
        CmPessoa,
        models.DO_NOTHING,
        related_name="edpessoavagavalidacao_cm_pessoa_responsavel_validacao_set",
        blank=True,
        null=True,
        verbose_name="Responsável pela validação",
    )
    ed_vaga = models.ForeignKey("EdVaga", models.DO_NOTHING, verbose_name="Vaga")
    pontuacao = models.FloatField(verbose_name="Pontuação")
    data = models.DateTimeField(verbose_name="Data da validação")

    class Meta:
        verbose_name = "(Editais) Pessoa validada"
        verbose_name_plural = "(Editais) Pessoas validadas"
        managed = False
        db_table = "ed_pessoa_vaga_validacao"

    @classmethod
    def validar_codigo_pelo_cpf(cls, cpf, codigo):
        from cead.messages import ERRO_HASH_INVALIDO
        from cead.ficha.messages import (
            ERRO_ED_PESSOA_VAGA_VALIDACAO_GEROU_FICHA_JA_EXISTE,
        )

        validacoes = cls.objects.filter(cm_pessoa__cpf=cpf)
        for validacao in validacoes:
            if validacao.codigo == codigo:
                if EdPessoaVagaGerouFicha.objects.filter(
                    ed_pessoa_vaga_validacao_id=validacao.id
                ).exists():
                    raise Exception(ERRO_ED_PESSOA_VAGA_VALIDACAO_GEROU_FICHA_JA_EXISTE)
                return validacao
        raise Exception(ERRO_HASH_INVALIDO)

    # A ficha so' podera' ser gerada se na URL tiver este codigo
    @property
    def codigo(self):
        pontuacao_str = (
            f"{self.pontuacao:.2f}" if self.pontuacao is not None else "0.00"
        )
        data_str = (
            self.data.strftime("%Y-%m-%d %H:%M:%S")
            if self.data
            else "0000-00-00 00:00:00"
        )

        base_str = (
            f"{self.id}"
            f"{self.cm_pessoa_id}"
            f"{self.cm_pessoa_responsavel_validacao_id or ''}"
            f"{self.ed_vaga_id}"
            f"{pontuacao_str}"
            f"{data_str}"
        )
        return hashlib.sha256(base_str.encode()).hexdigest()

    # Apenas para mostrar no admin
    def codigo_label(self):
        return self.codigo

    codigo_label.short_description = "Código da validação"


class EdVaga(models.Model):
    id = models.BigAutoField(primary_key=True)
    ed_edital = models.ForeignKey(EdEdital, models.DO_NOTHING, verbose_name="Edital")
    ac_polo = models.ForeignKey(
        AcPolo, models.DO_NOTHING, blank=True, null=True, verbose_name="Polo"
    )
    descricao = models.CharField(max_length=127, verbose_name="Descrição")
    quantidade = models.SmallIntegerField(
        blank=True, null=True, verbose_name="Quantidade de vagas"
    )

    def __str__(self):
        if self.descricao:
            return self.descricao
        return "-"

    class Meta:
        verbose_name = "(Editais) Vaga do edital"
        verbose_name_plural = "(Editais) Vagas dos editais"
        managed = False
        db_table = "ed_vaga"


class EdVagaCampoCheckbox(models.Model):
    id = models.BigAutoField(primary_key=True)
    ed_vaga = models.ForeignKey(EdVaga, models.DO_NOTHING, verbose_name="Vaga")
    ed_campo = models.ForeignKey(EdCampo, models.DO_NOTHING, verbose_name="Campo")
    pontuacao = models.SmallIntegerField(
        blank=True, null=True, verbose_name="Pontuação"
    )
    obrigatorio = models.BooleanField(verbose_name="Obrigatório?")
    assinado = models.BooleanField(verbose_name="Assinado?")

    class Meta:
        verbose_name = "(Editais) Checkbox da vaga"
        verbose_name_plural = "(Editais) Checkboxes das vagas"
        managed = False
        db_table = "ed_vaga_campo_checkbox"


class EdVagaCampoCombobox(models.Model):
    id = models.BigAutoField(primary_key=True)
    ed_vaga = models.ForeignKey(EdVaga, models.DO_NOTHING, verbose_name="Vaga")
    ed_campo = models.ForeignKey(EdCampo, models.DO_NOTHING, verbose_name="Campo")
    descricao = models.TextField(verbose_name="Descrição")
    ordem = models.SmallIntegerField()
    pontuacao = models.SmallIntegerField(
        blank=True, null=True, verbose_name="Pontuação"
    )
    obrigatorio = models.BooleanField(verbose_name="Obrigatório?")
    assinado = models.BooleanField(verbose_name="Assinado?")

    class Meta:
        verbose_name = "(Editais) Combobox da vaga"
        verbose_name_plural = "(Editais) Comboboxes das vagas"
        managed = False
        db_table = "ed_vaga_campo_combobox"


class EdVagaCampoDatebox(models.Model):
    id = models.BigAutoField(primary_key=True)
    ed_vaga = models.ForeignKey(EdVaga, models.DO_NOTHING, verbose_name="Vaga")
    ed_campo = models.ForeignKey(EdCampo, models.DO_NOTHING, verbose_name="Campo")
    fracao_pontuacao = models.FloatField(verbose_name="Fração de pontuação")
    multiplicador_fracao_pontuacao = models.SmallIntegerField(
        db_comment="Multiplicador em dias",
        verbose_name="Multiplicador em dias p/ pontuação",
    )
    pontuacao_maxima = models.FloatField(verbose_name="Pontuação máxima")
    obrigatorio = models.BooleanField(verbose_name="Obrigatório?")
    assinado = models.BooleanField(verbose_name="Assinado?")

    class Meta:
        verbose_name = "(Editais) Datebox da vaga"
        verbose_name_plural = "(Editais) Dateboxes das vagas"
        managed = False
        db_table = "ed_vaga_campo_datebox"


class EdVagaCota(models.Model):
    id = models.BigAutoField(primary_key=True)
    ed_vaga = models.ForeignKey(EdVaga, models.DO_NOTHING, verbose_name="Vaga")
    ed_cota = models.ForeignKey(EdCota, models.DO_NOTHING, verbose_name="Cota")

    def __str__(self):
        return f"Cota {self.ed_cota.cota} na vaga {self.ed_vaga.descricao}"

    class Meta:
        verbose_name = "(Editais) Associação entre vaga e cota"
        verbose_name_plural = "(Editais) Associações entre vagas e cotas"
        managed = False
        db_table = "ed_vaga_cota"


class FiDatafrequencia(models.Model):
    id = models.BigAutoField(primary_key=True)
    data_inicio = models.DateTimeField(blank=True, null=True)
    data_fim = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        if self.data_inicio and self.data_fim:
            tz = timezone("America/Sao_Paulo")
            data_inicio_tz = self.data_inicio.astimezone(tz)
            data_fim_tz = self.data_fim.astimezone(tz)
            return f"De {data_inicio_tz.strftime('%d/%m/%Y %H:%M')} até {data_fim_tz.strftime('%d/%m/%Y %H:%M')}"
        return "Sem informações de datas"

    def mes_ano_datafrequencia(self):
        if self.data_inicio:
            tz = timezone("America/Sao_Paulo")
            data_inicio_tz = self.data_inicio.astimezone(tz)
            return data_inicio_tz.strftime("%m/%Y")
        return "-"

    def ano_mes_datafrequencia(self):
        if self.data_inicio:
            tz = timezone("America/Sao_Paulo")
            data_inicio_tz = self.data_inicio.astimezone(tz)
            return data_inicio_tz.strftime("%Y_%m")
        return "-"

    class Meta:
        verbose_name = "(Financeiro) Período de lançamento de frequência"
        verbose_name_plural = "(Financeiro) Períodos de lançamento de frequências"
        managed = False
        db_table = "fi_datafrequencia"


class FiFuncaoBolsista(models.Model):
    id = models.BigAutoField(primary_key=True)
    funcao = models.CharField(max_length=31, verbose_name="Função do bolsista")
    ficha_uab = models.BooleanField(verbose_name="Pode gerar ficha UAB?")

    def __str__(self):
        if self.funcao:
            return self.funcao
        return "-"

    class Meta:
        verbose_name = "(Financeiro) Função do bolsista"
        verbose_name_plural = "(Financeiro) Funções dos bolsistas"

        managed = False
        db_table = "fi_funcao_bolsista"


class FiFuncaoBolsistaDeclaracao(models.Model):
    id = models.BigAutoField(primary_key=True)
    fi_funcao_bolsista = models.ForeignKey(
        FiFuncaoBolsista, models.DO_NOTHING, verbose_name="Função do bolsista"
    )
    item_declaracao = models.TextField(
        blank=True, null=True, verbose_name="Item da descrição"
    )

    def __str__(self):
        if self.item_declaracao:
            return self.item_declaracao
        return "-"

    class Meta:
        verbose_name = "(Financeiro) Item da declaração da ficha"
        verbose_name_plural = "(Financeiro) Itens da declaração da ficha"

        managed = False
        db_table = "fi_funcao_bolsista_declaracao"


# Motivos para deixar assim:
# 1) Mantem de forma simples o que o usuario realmente enviou
# 2) Estes dados nao sao utilizados em mais lugar nenhum
# 3) Força o usuário a lidar melhor com validação/invalidação de bolsista
# 4) Não permite "bagunça" de associar pessoas sem ficha (pagamentos ilegais/indevidos)
class FiPessoaFicha(models.Model):
    id = models.BigAutoField(primary_key=True)
    cm_pessoa = models.ForeignKey(CmPessoa, models.DO_NOTHING, verbose_name="Bolsista")
    ed_edital = models.ForeignKey(
        EdEdital, models.DO_NOTHING, blank=True, null=True, verbose_name="Edital"
    )
    fi_funcao_bolsista = models.ForeignKey(
        FiFuncaoBolsista,
        models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Função do bolsista",
    )
    ac_curso_oferta = models.ForeignKey(
        AcCursoOferta, models.DO_NOTHING, blank=True, null=True, verbose_name="Oferta"
    )
    cm_municipio = models.ForeignKey(
        CmMunicipio,
        models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Município de nascimento",
        db_column="cm_municipio_id",
    )
    data_nascimento = models.DateField(
        blank=True, null=True, verbose_name="Data de nascimento"
    )
    sexo = models.CharField(max_length=1, blank=True, null=True, verbose_name="Sexo")
    profissao = models.CharField(
        max_length=127, blank=True, null=True, verbose_name="Profissão"
    )
    tipo_documento = models.CharField(
        max_length=3, blank=True, null=True, verbose_name="Tipo de documento"
    )
    numero_documento = models.CharField(
        max_length=31, blank=True, null=True, verbose_name="Número do documento"
    )
    orgao_expedidor = models.CharField(
        max_length=31, blank=True, null=True, verbose_name="Órgão expedidor"
    )
    data_emissao = models.DateField(
        blank=True, null=True, verbose_name="Data de emissão"
    )
    estado_civil = models.CharField(
        max_length=15, blank=True, null=True, verbose_name="Estado civil"
    )
    nome_conjuge = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Nome do cônjuge"
    )
    nome_pai = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Nome do pai"
    )
    nome_mae = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Nome da mãe"
    )
    area_ultimo_curso_superior = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Área do último curso superior",
    )
    ultimo_curso_titulacao = models.CharField(
        max_length=127, blank=True, null=True, verbose_name="Titulação do último curso"
    )
    instituicao_titulacao = models.CharField(
        max_length=127, blank=True, null=True, verbose_name="Instituição da titulação"
    )
    data_inicio_vinculacao = models.DateField(
        blank=True, null=True, verbose_name="Data de início da vinculação"
    )
    data_fim_vinculacao = models.DateField(
        blank=True, null=True, verbose_name="Data de fim da vinculação"
    )

    class Meta:
        verbose_name = "(Financeiro) Ficha"
        verbose_name_plural = "(Financeiro) Fichas"
        managed = False
        db_table = "fi_pessoa_ficha"


class FiFrequencia(models.Model):
    id = models.BigAutoField(primary_key=True)
    cm_pessoa = models.ForeignKey(CmPessoa, models.DO_NOTHING, verbose_name="Bolsista")
    cm_pessoa_coordenador = models.ForeignKey(
        CmPessoa,
        models.DO_NOTHING,
        related_name="fifrequencia_cm_pessoa_coordenador_set",
        verbose_name="Coordenador",
    )
    fi_datafrequencia = models.ForeignKey(
        FiDatafrequencia, models.DO_NOTHING, verbose_name="Período"
    )
    ac_curso_oferta = models.ForeignKey(
        AcCursoOferta, models.DO_NOTHING, verbose_name="Oferta do curso"
    )
    fi_funcao_bolsista = models.ForeignKey(
        FiFuncaoBolsista, models.DO_NOTHING, verbose_name="Função do bolsista"
    )
    data = models.DateTimeField(verbose_name="Data do lançamento")

    class Meta:
        verbose_name = "(Financeiro) Frequência"
        verbose_name_plural = "(Financeiro) Frequências"
        managed = False
        db_table = "fi_frequencia"


class FiFrequenciaDisciplina(models.Model):
    id = models.BigAutoField(primary_key=True)
    fi_frequencia = models.ForeignKey(FiFrequencia, models.DO_NOTHING)
    ac_disciplina = models.ForeignKey(AcDisciplina, models.DO_NOTHING)

    class Meta:
        verbose_name = "(Financeiro) Frequência - disciplina lançada para o bolsista"
        verbose_name_plural = (
            "(Financeiro) Frequências - disciplinas lançadas para os bolsistas"
        )
        managed = False
        db_table = "fi_frequencia_disciplina"


class FiFrequenciaMoodle(models.Model):
    id = models.BigAutoField(primary_key=True)
    fi_datafrequencia = models.ForeignKey(FiDatafrequencia, models.DO_NOTHING)
    cm_pessoa = models.ForeignKey(CmPessoa, models.DO_NOTHING)
    moodle_id = models.CharField(max_length=11)
    ultimo_acesso = models.DateTimeField(blank=True, null=True)
    data_consulta = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "(Financeiro) Frequência - acesso do bolsista ao Moodle"
        verbose_name_plural = (
            "(Financeiro) Frequências - acessos dos bolsistas ao Moodle"
        )
        managed = False
        db_table = "fi_frequencia_moodle"


class FiEditalFuncaoOferta(models.Model):
    # O sistema antigo nao refletia a realidade da bolsa: todos os bolsistas
    # possuiam relacao com oferta, o que nao e' realidade dos fatos
    # Coordenadores gerais e adjuntos nao possuem relacao com oferta de curso
    # A base antiga foi migrada como estava, mas aqui, em FiEditalFuncaoOferta,
    # a modelagem esta' correta: ac_curso_oferta pode ser NULL
    # O que acontecia no sistema antigo, provavelmente: relacionava-se o
    # coordenador geral/adjunto com o ultimo curso dele, ou havia curso inventado
    # na base, que nao foi migrado
    # Um coordenador do curso X, alcado a coordenador geral, mantinha o registro
    # de estar associado ao curso X
    # Estou me baseando, obviamente, na portaria 309/2024 da CAPES, mas pelo que
    # pesquisei, me parece que nenhuma universidade pensou no problema
    #
    # A solucao para unicidade nao e' padrao no SQL 92 e funciona apenas em PostgreSQL 15+
    # CREATE UNIQUE INDEX fi_edital_funcao_oferta_unique ON sistemascead.fi_edital_funcao_oferta
    # USING btree (ed_edital_id, fi_funcao_bolsista_id, ac_curso_oferta_id) NULLS NOT DISTINCT;
    id = models.BigAutoField(primary_key=True)
    ed_edital = models.ForeignKey(EdEdital, models.DO_NOTHING, verbose_name="Edital")
    fi_funcao_bolsista = models.ForeignKey(
        FiFuncaoBolsista, models.DO_NOTHING, verbose_name="Função"
    )
    ac_curso_oferta = models.ForeignKey(
        AcCursoOferta, models.DO_NOTHING, null=True, blank=True, verbose_name="Oferta"
    )

    class Meta:
        verbose_name = (
            "(Financeiro) Associação entre edital, função da ficha e oferta do curso"
        )
        verbose_name_plural = "(Financeiro) Associações entre editais, funções das fichas e ofertas dos cursos"
        managed = False
        db_table = "fi_edital_funcao_oferta"


class TrTermo(models.Model):
    id = models.BigAutoField(primary_key=True)
    termo = models.TextField()

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "(Transmissão) Termo de transmissão"
        verbose_name_plural = "(Transmissão) Termos de transmissões"
        managed = False
        db_table = "tr_termo"


class TrEspacoFisico(models.Model):
    id = models.BigAutoField(primary_key=True)
    espaco_fisico = models.CharField(max_length=63, verbose_name="Espaço físico")
    dias_pre_transmissao = models.SmallIntegerField(
        blank=True, null=True, verbose_name="Intervalo (dias) anterior (logística)"
    )
    dias_pos_transmissao = models.SmallIntegerField(
        blank=True, null=True, verbose_name="Intervalo (dias) posterior (logística)"
    )
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    ativo = models.BooleanField(verbose_name="Ativo?")

    def __str__(self):
        return str(self.espaco_fisico)

    class Meta:
        verbose_name = "(Transmissão) Características do espaço físico para transmissão"
        verbose_name_plural = (
            "(Transmissão) Características do espaço físico para transmissões"
        )
        managed = False
        db_table = "tr_espaco_fisico"


class TrDisponibilidadeEquipe(models.Model):
    id = models.BigAutoField(primary_key=True)
    dia_semana = models.CharField(
        max_length=1,
        choices=DIAS_SEMANA,
        db_comment="isodow() do pgsql",
        verbose_name="Dia da semana",
    )
    inicio = models.TimeField(verbose_name="Início")
    fim = models.TimeField(verbose_name="Fim")

    class Meta:
        managed = False
        db_table = "tr_disponibilidade_equipe"
        verbose_name = "(Transmissão) Dia e horário disponível da equipe"
        verbose_name_plural = "(Transmissão) Dias e horários disponíveis da equipe"


class TrIndisponibilidadeEquipe(models.Model):
    id = models.BigAutoField(primary_key=True)
    data = models.DateField(unique=True, verbose_name="Data indisponível")

    class Meta:
        managed = False
        db_table = "tr_indisponibilidade_equipe"
        verbose_name = "(Transmissão) Dia indisponível da equipe"
        verbose_name_plural = "(Transmissão) Dias indisponíveis da equipe"


class TrTransmissao(models.Model):
    id = models.BigAutoField(primary_key=True)
    tr_termo = models.ForeignKey(TrTermo, models.DO_NOTHING, verbose_name="Termo")
    cm_pessoa = models.ForeignKey(
        CmPessoa,
        models.DO_NOTHING,
        db_comment="Requisitante",
        verbose_name="Requisitante",
    )
    tr_espaco_fisico = models.ForeignKey(
        TrEspacoFisico, models.DO_NOTHING, verbose_name="Espaço físico"
    )
    observacao = models.TextField(verbose_name="Observação")

    def assinatura_digital(self):
        from cead.transmissao.utils import hash_transmissao

        return hash_transmissao(self)

    assinatura_digital.short_description = "Assinatura digital"

    def __str__(self):
        return f"{self.tr_espaco_fisico} ({self.cm_pessoa})"

    class Meta:
        managed = False
        db_table = "tr_transmissao"
        verbose_name = "(Transmissão) Pedido de transmissão"
        verbose_name_plural = "(Transmissão) Pedidos de transmissões"


class TrTransmissaoHorario(models.Model):
    id = models.BigAutoField(primary_key=True)
    tr_transmissao = models.ForeignKey(
        TrTransmissao, models.DO_NOTHING, verbose_name="Transmissão"
    )
    inicio = models.DateTimeField(verbose_name="Início")
    fim = models.DateTimeField(verbose_name="Fim")

    class Meta:
        managed = False
        db_table = "tr_transmissao_horario"
        verbose_name = "(Transmissão) Horário do pedido de transmissão"
        verbose_name_plural = "(Transmissão) Horários dos pedidos de transmissões"


class TrTransmissaoEmail(models.Model):
    id = models.BigAutoField(primary_key=True)
    email = models.CharField(unique=True, max_length=254, verbose_name="E-mail")
    tipo_email_envio = models.CharField(
        max_length=3,
        choices=[
            ("cc", "Com cópia"),
            ("cco", "Com cópia oculta"),
        ],
        blank=True,
        null=True,
        verbose_name="Tipo de envio",
    )

    class Meta:
        managed = False
        db_table = "tr_transmissao_email"
        verbose_name = (
            "(Transmissão) E-mail para envio de alerta de pedido de transmissão"
        )
        verbose_name_plural = (
            "(Transmissão) E-mails para envios de alertas de pedidos de transmissões"
        )


class TrTransmissaoRecusada(models.Model):
    id = models.BigAutoField(primary_key=True)
    tr_transmissao = models.ForeignKey(
        TrTransmissao, models.DO_NOTHING, verbose_name="Transmissão"
    )
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")

    class Meta:
        managed = False
        db_table = "tr_transmissao_recusada"
        verbose_name = "(Transmissão) Transmissão recusada"
        verbose_name_plural = "(Transmissão) Transmissões recusadas"


class TrLimites(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    maximo_por_mes = models.SmallIntegerField(
        verbose_name="Máximo de transmissões por mês"
    )
    maximo_por_semana = models.SmallIntegerField(
        verbose_name="Máximo de transmissões por semana"
    )
    maximo_dias_na_semana = models.SmallIntegerField(
        verbose_name="Máximo de dias de transmissão por semana"
    )
    limite_por_pessoa = models.SmallIntegerField(
        verbose_name="Limite de pedidos ativos por pessoa"
    )
    dias_de_antecedencia = models.SmallIntegerField(
        verbose_name="Dias a partir de hoje de antecedência para agendamento"
    )
    dias_de_agenda_aberta = models.SmallIntegerField(
        verbose_name="Dias a partir de hoje abertos na agenda"
    )
    evento_passando_de_semana = models.BooleanField(
        verbose_name="O mesmo evento pode se estender por mais de uma semana?"
    )

    class Meta:
        managed = False
        db_table = "tr_limites"
        verbose_name = "(Transmissão) Limites de pedido de transmissão"
        verbose_name_plural = "(Transmissão) Limites de pedidos de transmissões"
