#!/usr/bin/python

# http://qiita.com/tt_yamaguchi/items/fcac45e08ca05020a2ff
# こちらを少し修正しました
# AMIがあって落ちる場合を考慮してtryにした
# iam-roleに対応

import boto.ec2.connection
import urllib2

res = urllib2.urlopen('http://169.254.169.254/latest/meta-data/local-hostname')
region = res.read().split(".")[1]

ec2 = boto.ec2.connect_to_region(region)

instances = [i for r in ec2.get_all_instances(filters={'tag-key':'backup', 'tag-value':'ON'}) for i in r.instances]

for instance in instances:
  print "backup instance: %s" % instance.id

  generation = int(instance.tags.get('generation'))
  print "backup generation: %s" % generation

  volumes = ec2.get_all_volumes(filters={'attachment.instance-id': instance.id})

  for v in volumes:
    print "create snapshot: %s" % v.id
    v.create_snapshot(description='snapshot: ' + v.id)

    snaps = v.snapshots()
    sorted_snaps = sorted(snaps, key=lambda snap: snap.start_time, reverse=True)
    for i, snap in enumerate(sorted_snaps):
      if i >= generation:
        print "delete snapshot: %s" % snap.id

        try:
            snap.delete()
            print "delete snapshot: %s" % snap.id
        except:
            print 'cannot: delete snapshot: %s' % snap.id
