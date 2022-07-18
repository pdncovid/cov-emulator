from backend.python.Logger import Logger
from backend.python.MovementEngine import MovementEngine
from backend.python.enums import Mobility
from backend.python.point.Transporter import Transporter
from backend.python.transport.Movement import Movement


class MovementByTransporter(Movement):
    all_instances = []

    def get_in_transport_transmission_p(self):
        raise NotImplementedError()

    # override
    def get_description_dict(self):
        d = super().get_description_dict()
        return d

    # override
    def add_point_to_transport(self, point):
        super().add_point_to_transport(point)

    # # override
    # def transport_point(self, point, destination_xy):
    #     if not isinstance(point, Transporter):
    #         return
    #
    #     super().transport_point(point, destination_xy)

    def __init__(self, class_info, **kwargs):
        super().__init__(class_info, **kwargs)
        MovementByTransporter.all_instances.append(self)

    def find_feasibility(self, tr, path2next_tar):
        hops2reach = [1e10 for _ in path2next_tar]
        dist_by_disp = [1e10 for _ in path2next_tar]

        for i in range(len(path2next_tar)):
            tar = path2next_tar[i]
            hops = 0
            displacement = tr.get_current_location().get_distance_to(tar)
            distance = 0

            flag = -1
            start_j , end_j = -1, -1
            for j in range(len(tr.route_rep_all_stops)):
                if tr.get_current_location() == tr.route_rep_all_stops[j] or tar == tr.route_rep_all_stops[j]:
                    flag += 1  # found start or end
                if flag == 0:
                    start_j = j
                    hops += 1
                    if j == 0:
                        pass
                    else:
                        distance += tr.route_rep_all_stops[j].get_distance_to(tr.route_rep_all_stops[j - 1])
                if flag == 1:
                    end_j = j
                    dist_by_disp[i] = distance / (displacement + 1e-10)
                    hops2reach[i] = hops
                    break
            else:
                hops2reach[i] = 1e10
                dist_by_disp[i] = 1e10

            if len(tr.route) - tr.current_target_idx - 2 < end_j - start_j:  # tr ends route before going to destination
                # Logger.log("# tr ends route before going to destination",'c')
                hops2reach[i] = 1e10
                dist_by_disp[i] = 1e10

        Logger.log(f"Path to target {list(map(str, path2next_tar))} {hops2reach}", 'i')
        des = None
        best = 1e10

        def cost(arr, x):
            return arr[x] * (len(arr) - x)

        for i in range(len(hops2reach)):
            if hops2reach[i] == 1e10:
                continue
            # if dist_by_disp[i] > 1000:  # TODO: Whats the optimal value
            #     continue
            c = dist_by_disp[i]  # *cost(hops2reach, i)
            if c < best:
                best = c
                des = path2next_tar[i]
        return best, des

    def try_to_latch_people(self, location, transporter):
        transporters = [transporter]
        # commented below for speed test. Check if other transporters need to be checked
        # for p in location.points:
        #     if isinstance(p, Transporter):
        #         transporters.append(p)

        for p in location.points:  # check for all points in the current location
            if isinstance(p, Transporter):
                continue
            if p.latched_to is not None:
                continue
            path2next_tar = MovementEngine.get_next_target_path(p)
            possible_transporters = []
            for transporter in transporters:
                if p.all_movement_ids[p.ID] != p.all_movement_ids[transporter.ID]:  # not in same movement method!
                    continue
                cost, des = self.find_feasibility(transporter, path2next_tar)
                if des is not None:
                    possible_transporters.append((cost, transporter, des))
            if len(possible_transporters) == 0:
                Logger.log("No one to latch", 'i')
                continue
            possible_transporters.sort(key=lambda x: x[0])

            for i in range(len(possible_transporters)):
                (cost, transporter, destination) = possible_transporters[i]
                if transporter.latch(p, destination):
                    Logger.log(
                        f"{p.ID} in {self} latched to transporter {transporter.ID} at {location} and will goto {destination.name}",
                        'd')
                    break
