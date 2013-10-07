import datetime

class Storage():


    def read_course_base(self):
        """Retrieves latest course base.

        :return: list of Courses or None if storage is empty.
        """
        pass

    def last_update_date(self):
        """
        :return: retrieval date of latest course base or None if storage is empty.
        """
        pass

    def store_course_base(self, course_json):
        """
        :param course_json: json string containing scraped course information
        """
        pass