from backend.python.Logger import Logger
from backend.python.MovementEngine import MovementEngine
from backend.python.enums import Mobility
from backend.python.point.Transporter import Transporter
from backend.python.transport.Movement import Movement


class MovementByTransporter(Movement):
    all_instances = []

    def get_in_transport_transmission_p(self):
        raise NotImplementedError()

    def __init__(self, velocity_cap: float, mobility_pattern: Mobility):
        super().__init__(velocity_cap, mobility_pattern)
        MovementByTransporter.all_instances.append(self)
    # override
    def get_description_dict(self):
        d = super().get_description_dict()
        return d

    # override
    def add_point_to_transport(self, point, target_location):
        super().add_point_to_transport(point, target_location)
        if isinstance(point, Transporter):
            self.try_to_latch_people(point)

    # override
    def transport_point(self, point, destination_xy):
        if not isinstance(point, Transporter):
            return

        super().transport_point(point, destination_xy)

    def find_feasibility(self, tr, path2next_tar):
        hops2reach = [-1. for _ in path2next_tar]

        for i in range(len(path2next_tar)):
            tar = path2next_tar[i]
            hops = 0
            for j in range(tr.current_target_idx, len(tr.route)):
                hops += 1
                if tar == tr.route[j].loc:
                    break
            else:
                hops = -1
            hops2reach[i] = hops
        Logger.log(f"Path to target {list(map(str, path2next_tar))} {hops2reach}", 'e')
        des = None
        best = 1e10

        def cost(arr, x):
            return arr[x] * (len(arr) - x)

        for i in range(len(hops2reach)):
            if hops2reach[i] < 0:
                continue
            if cost(hops2reach, i) < best:
                best = cost(hops2reach, i)
                des = path2next_tar[i]
        return best, des

    def try_to_latch_person(self, p, transporter):
        possible_transporters = []  # element - (cost, transporter, destination)
        path2next_tar = MovementEngine.get_next_target_path(p)
        # for pl in p.get_current_location().points:
        #     if isinstance(pl, Transporter):
        pl = transporter
        Logger.log(f"Trying to latch {p.ID} ({path2next_tar[-1].name}) in {self} to transporter "
                   f"{pl.ID} ({list(map(str, pl.route))}) {pl.get_current_location()}", 'e')
        cost, des = self.find_feasibility(pl, path2next_tar)
        if des is not None:
            possible_transporters.append((cost, pl, des))

        if len(possible_transporters) == 0:
            Logger.log("No one to latch", 'e')
            return
        possible_transporters.sort(key=lambda x: x[0])

        for i in range(len(possible_transporters)):
            (cost, transporter, destination) = possible_transporters[i]
            if transporter.latch(p, destination):
                Logger.log(f"{p.ID} in {self} latched to transporter {transporter.ID} and will goto {destination.name}",
                           'c')
                break

    def try_to_latch_people(self, transporter):
        # todo find people waiting for long time and make them walk
        for p in transporter.get_current_location().points:  # check for all points in the current location
            if isinstance(p, Transporter):
                continue
            if p.all_movement_ids[p.ID] != p.all_movement_ids[transporter.ID]:  # not in same movement method!
                continue
            if not p.latched_to:
                self.try_to_latch_person(p, transporter)
