#
# Copyright (c) 2006-2013 Wade Alcorn - wade@bindshell.net
# Browser Exploitation Framework (BeEF) - http://beefproject.com
# See the file 'doc/COPYING' for copying permission
#
class Detect_vlc < BeEF::Core::Command

	def post_execute
		content = {}
		content['vlc'] = @datastore['vlc']
		save content
	end

end
