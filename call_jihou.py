# -*- coding: utf-8 -*-
import slacker_miku.jihou as sla_jihou
import beluga_miku.jihou as bel_jihou

def post_time():
	bel_jihou.post_time_beluga()
	sla_jihou.post_time_slack()

if __name__ == "__main__":
    post_time()
