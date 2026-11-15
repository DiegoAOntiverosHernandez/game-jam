"""Mundo ECS: guarda entidades (ids), componentes y sistemas."""


class Mundo:
    def __init__(self):
        self._siguiente_id = 0
        self.componentes = {}  # tipo de componente -> {id_entidad: componente}
        self.sistemas = []

    def crear_entidad(self, *componentes):
        id_entidad = self._siguiente_id
        self._siguiente_id += 1
        for componente in componentes:
            self.agregar_componente(id_entidad, componente)
        return id_entidad

    def agregar_componente(self, id_entidad, componente):
        self.componentes.setdefault(type(componente), {})[id_entidad] = componente

    def obtener(self, id_entidad, tipo):
        return self.componentes.get(tipo, {}).get(id_entidad)

    def entidades_con(self, *tipos):
        """Devuelve (id, [componentes]) de las entidades que tienen todos los tipos."""
        primeros = self.componentes.get(tipos[0], {})
        for id_entidad in list(primeros):
            if all(id_entidad in self.componentes.get(t, {}) for t in tipos):
                yield id_entidad, [self.componentes[t][id_entidad] for t in tipos]

    def eliminar_entidad(self, id_entidad):
        for almacen in self.componentes.values():
            almacen.pop(id_entidad, None)

    def agregar_sistema(self, sistema):
        self.sistemas.append(sistema)

    def actualizar(self, dt):
        for sistema in self.sistemas:
            sistema.actualizar(self, dt)