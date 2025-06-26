def get_salas():
    return ["Sala 1", "Sala 2", "Sala 3"]

def formatar_agendamento(agendamento):
    id, nome, sala, data, hora_inicio, hora_fim = agendamento
    return f"{data} | {hora_inicio} - {hora_fim} | {sala} | {nome}"
