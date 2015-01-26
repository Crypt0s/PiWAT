#
# Copyright (c) 2006-2013 Wade Alcorn - wade@bindshell.net
# Browser Exploitation Framework (BeEF) - http://beefproject.com
# See the file 'doc/COPYING' for copying permission
#
module BeEF
  module Core
    module Models

      class Massmailer

        include DataMapper::Resource

        storage_names[:default] = 'extension_seng_massmailer'

        property :id, Serial

        #todo fields
      end

    end
  end
end
