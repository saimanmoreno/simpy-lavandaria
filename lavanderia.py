import random
import simpy

contaClientes = 0           # conta clientes que chegaram no sistema


def distributions(tipo):
    # função que armazena as distribuições utilizadas no modelo
    return {
        'chegadas': random.expovariate(1.0/5.0),
        'lavar': 20,
        'carregar': random.uniform(1, 4),
        'descarregar': random.uniform(1, 2),
        'secar': random.uniform(9, 12),
    }.get(tipo, 0.0)


def chegadaClientes(env, lavadoras, cestos, secadoras):
    # função que gera a chegada de clientes
    global contaClientes

    contaClientes = 0
    while True:
        contaClientes += 1
        yield env.timeout(distributions('chegadas'))
        print("%.1f chegada do cliente %s" % (env.now, contaClientes))
        # chamada do processo de lavagem e secagem
        env.process(lavaSeca(env, "Cliente %s" %
                             contaClientes, lavadoras, cestos, secadoras))


def lavaSeca(env, cliente, lavadoras, cestos, secadoras):
    # função que processa a operação de cada cliente dentro da lavanderia
    global utilLavadora, tempoEsperaLavadora, contaLavadora

    # ocupa a lavadora
    req1 = lavadoras.request()
    yield req1
    print("%.1f %s ocupa lavadora" % (env.now, cliente))
    yield env.timeout(distributions('lavar'))

    # antes de retirar da lavadora, pega um cesto
    req2 = cestos.request()
    yield req2
    print("%.1f %s ocupa cesto" % (env.now, cliente))
    yield env.timeout(distributions('carregar'))

    # libera a lavadora, mas não o cesto
    lavadoras.release(req1)
    print("%.1f %s desocupa lavadora" % (env.now, cliente))

    # ocupa a secadora antes de liberar o cesto
    req3 = secadoras.request()
    yield req3
    print("%.1f %s ocupa secadora" % (env.now, cliente))
    yield env.timeout(distributions('descarregar'))

    # libera o cesto mas não a secadora
    cestos.release(req2)
    print("%.1f %s desocupa cesto" % (env.now, cliente))
    yield env.timeout(distributions('secar'))

    # pode liberar a secadora
    print("%.1f %s desocupa secadora" % (env.now, cliente))
    secadoras.release(req3)


print('\n')
random.seed(10)
env = simpy.Environment()
lavadoras = simpy.Resource(env, capacity=3)
cestos = simpy.Resource(env, capacity=2)
secadoras = simpy.Resource(env, capacity=1)
env.process(chegadaClientes(env, lavadoras, cestos, secadoras))

env.run(until=50)

print('\n')