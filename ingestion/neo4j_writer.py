from neo4j import GraphDatabase
from config.settings import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


class Neo4jWriter:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def write_scene(self, frames):
        with self.driver.session() as session:
            # Create ego vehicle node once
            session.execute_write(self._create_ego)

            for frame in frames:
                session.execute_write(self._write_frame, frame)
                print(f"  Wrote frame {frame['token'][:8]}... "
                      f"| {len(frame['objects'])} objects")

    @staticmethod
    def _create_ego(tx):
        tx.run("""
            MERGE (e:EgoVehicle {id: 'ego'})
            SET e.type = 'EgoVehicle'
        """)

    @staticmethod
    def _write_frame(tx, frame):
        # Create Frame node
        tx.run("""
            MERGE (f:Frame {token: $token})
            SET f.timestamp = $timestamp,
                f.ego_x = $ex,
                f.ego_y = $ey,
                f.ego_z = $ez
        """,
            token=frame['token'],
            timestamp=frame['timestamp'],
            ex=frame['ego_translation'][0],
            ey=frame['ego_translation'][1],
            ez=frame['ego_translation'][2],
        )

        # Bulk upsert all objects in this frame
        tx.run("""
            UNWIND $objects AS obj
            MERGE (o:Object {token: obj.token})
            SET o.category   = obj.category,
                o.x          = obj.x,
                o.y          = obj.y,
                o.z          = obj.z,
                o.rel_x      = obj.rel_x,
                o.rel_y      = obj.rel_y,
                o.vel_x      = obj.vel_x,
                o.vel_y      = obj.vel_y,
                o.instance_token = obj.instance_token,
                o.last_seen  = obj.timestamp
        """,
            objects=[{**o, 'timestamp': frame['timestamp'],
                      'vel_x': o['velocity'][0],
                      'vel_y': o['velocity'][1]}
                     for o in frame['objects']]
        )

        # Link objects to their frame
        tx.run("""
            UNWIND $tokens AS token
            MATCH (o:Object {token: token}),
                  (f:Frame {token: $frame_token})
            MERGE (o)-[:IN_FRAME]->(f)
        """,
            tokens=[o['token'] for o in frame['objects']],
            frame_token=frame['token']
        )

        # Create IS_NEAR edges from ego to close objects
        tx.run("""
            UNWIND $objects AS obj
            MATCH (e:EgoVehicle {id: 'ego'}),
                  (o:Object {token: obj.token})
            WHERE obj.distance < 30
            MERGE (e)-[r:IS_NEAR]->(o)
            SET r.distance  = obj.distance,
                r.timestamp = obj.timestamp
        """,
            objects=[{
                'token': o['token'],
                'distance': (o['rel_x']**2 + o['rel_y']**2) ** 0.5,
                'timestamp': frame['timestamp']
            } for o in frame['objects']]
        )