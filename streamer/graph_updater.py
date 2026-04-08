from neo4j import GraphDatabase
from streamer.relations import classify_relation, compute_distance
from config.settings import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


class GraphUpdater:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
        self.active_tokens = set()
        self._ensure_ego()

    def close(self):
        self.driver.close()

    def _ensure_ego(self):
        with self.driver.session() as session:
            session.run("""
                MERGE (e:EgoVehicle {id: 'ego'})
                SET e.type = 'EgoVehicle'
            """)

    def update(self, frame):
        new_tokens = {o['token'] for o in frame['objects']}

        with self.driver.session() as session:
            # 1. Upsert all objects in this frame
            session.execute_write(self._upsert_objects, frame)

            # 2. Remove all current ego edges
            session.execute_write(self._clear_ego_edges)

            # 3. Recompute and write fresh edges
            session.execute_write(self._write_relations, frame)

            # 4. Remove objects that disappeared
            stale = self.active_tokens - new_tokens
            if stale:
                session.execute_write(self._remove_stale, stale)

            # 5. Update current frame marker on ego
            session.execute_write(self._update_ego, frame)

        self.active_tokens = new_tokens

        return {
            'frame_token': frame['token'],
            'timestamp':   frame['timestamp'],
            'active':      len(new_tokens),
            'removed':     len(self.active_tokens - new_tokens)
                           if self.active_tokens else 0,
        }

    @staticmethod
    def _upsert_objects(tx, frame):
        tx.run("""
            UNWIND $objects AS obj
            MERGE (o:Object {token: obj.token})
            SET o.category       = obj.category,
                o.x              = obj.x,
                o.y              = obj.y,
                o.z              = obj.z,
                o.rel_x          = obj.rel_x,
                o.rel_y          = obj.rel_y,
                o.vel_x          = obj.vel_x,
                o.vel_y          = obj.vel_y,
                o.instance_token = obj.instance_token,
                o.last_seen      = obj.timestamp,
                o.stale          = false
        """,
            objects=[{
                **o,
                'vel_x':     o['velocity'][0],
                'vel_y':     o['velocity'][1],
                'timestamp': frame['timestamp'],
            } for o in frame['objects']]
        )

    @staticmethod
    def _clear_ego_edges(tx):
        tx.run("""
            MATCH (e:EgoVehicle {id: 'ego'})-[r]->()
            DELETE r
        """)

    @staticmethod
    def _write_relations(tx, frame):
        relations = []

        for obj in frame['objects']:
            dist = compute_distance(
                (obj['rel_x'], obj['rel_y'])
            )
            rel = classify_relation(
                obj['rel_x'], obj['rel_y'], dist
            )
            if rel is None:
                continue

            relations.append({
                'token':     obj['token'],
                'distance':  rel['distance'],
                'zone':      rel['zone'],
                'direction': rel['direction'],
                'timestamp': frame['timestamp'],
            })

        if relations:
            tx.run("""
                UNWIND $relations AS rel
                MATCH (e:EgoVehicle {id: 'ego'}),
                      (o:Object {token: rel.token})
                MERGE (e)-[r:IS_NEAR]->(o)
                SET r.distance  = rel.distance,
                    r.zone      = rel.zone,
                    r.direction = rel.direction,
                    r.timestamp = rel.timestamp
            """, relations=relations)

    @staticmethod
    def _remove_stale(tx, stale_tokens):
        tx.run("""
            UNWIND $tokens AS token
            MATCH (o:Object {token: token})
            SET o.stale = true
        """, tokens=list(stale_tokens))

        tx.run("""
            UNWIND $tokens AS token
            MATCH (e:EgoVehicle {id: 'ego'})-[r]->(o:Object {token: token})
            DELETE r
        """, tokens=list(stale_tokens))

    @staticmethod
    def _update_ego(tx, frame):
        tx.run("""
            MATCH (e:EgoVehicle {id: 'ego'})
            SET e.x         = $x,
                e.y         = $y,
                e.timestamp = $timestamp
        """,
            x=frame['ego_translation'][0],
            y=frame['ego_translation'][1],
            timestamp=frame['timestamp'],
        )