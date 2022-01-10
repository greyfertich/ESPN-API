require 'date'
require_relative 'team'

class Game
  attr_reader :id, :name, :date, :home_team, :away_team
  def initialize(id, name, date, home_team, away_team)
    @id = id
    @name = name
    @date = DateTime.strptime(date, '%Y-%m-%dT%H:%M%Z').to_time
    @home_team = home_team
    @away_team = away_team
  end
  def is_live?
    current_time = DateTime.now.to_time
    return (current_time >= @date and ((current_time - @date) / 3600) <= 5)
  end
end


# DateTime.strptime('2001-02-03T04:05:06+07:00', '%Y-%m-%dT%H:%M%Z')
                          #=> #<DateTime: 2001-02-03T04:05:06+07:00 ...>