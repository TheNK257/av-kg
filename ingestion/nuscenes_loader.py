from nuscenes.nuscenes import NuScenes
from config.settings import NUSCENES_DATAROOT, NUSCENES_VERSION


def get_nusc():
    return NuScenes(
        version=NUSCENES_VERSION,
        dataroot=NUSCENES_DATAROOT,
        verbose=False
    )


def get_ego_pose(nusc, sample):
    sd_token = sample['data']['LIDAR_TOP']
    sd = nusc.get('sample_data', sd_token)
    ep = nusc.get('ego_pose', sd['ego_pose_token'])
    return ep['translation'], ep['rotation']


def parse_frame(nusc, sample):
    ego_translation, ego_rotation = get_ego_pose(nusc, sample)

    objects = []
    for ann_token in sample['anns']:
        ann = nusc.get('sample_annotation', ann_token)
        instance = nusc.get('instance', ann['instance_token'])

        pos = ann['translation']
        rel_x = pos[0] - ego_translation[0]
        rel_y = pos[1] - ego_translation[1]

        objects.append({
            'token':      ann_token,
            'category':   ann['category_name'],
            'x':          round(pos[0], 3),
            'y':          round(pos[1], 3),
            'z':          round(pos[2], 3),
            'rel_x':      round(rel_x, 3),
            'rel_y':      round(rel_y, 3),
            'size':       ann['size'],
            'velocity':   nusc.box_velocity(ann_token)[:2].tolist(),
            'instance_token': ann['instance_token'],
        })

    return {
        'token':           sample['token'],
        'timestamp':       sample['timestamp'],
        'ego_translation': ego_translation,
        'ego_rotation':    ego_rotation,
        'objects':         objects,
    }


def iter_scene(nusc, scene_index=0):
    scene = nusc.scene[scene_index]
    sample_token = scene['first_sample_token']

    while sample_token:
        sample = nusc.get('sample', sample_token)
        yield parse_frame(nusc, sample)
        sample_token = sample['next']


if __name__ == "__main__":
    nusc = get_nusc()

    print(f"Total scenes: {len(nusc.scene)}\n")

    for i, frame in enumerate(iter_scene(nusc, scene_index=0)):
        print(f"Frame {i+1} | timestamp: {frame['timestamp']}")
        print(f"  Ego position: {frame['ego_translation']}")
        print(f"  Objects: {len(frame['objects'])}")
        for obj in frame['objects'][:3]:
            print(f"    [{obj['category']}] "
                  f"rel_pos=({obj['rel_x']}, {obj['rel_y']}) "
                  f"vel={obj['velocity']}")
        print()